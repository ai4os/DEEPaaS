# -*- coding: utf-8 -*-

# Copyright 2018 Spanish National Research Council (CSIC)
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import io
import mimetypes
import os
import shutil
import tempfile

import fastapi
import fastapi.encoders
import fastapi.exceptions
import marshmallow
import starlette.background
import starlette.datastructures

from deepaas.api.v2 import responses
from deepaas.api.v2 import utils
from deepaas import log
from deepaas import model

LOG = log.getLogger(__name__)


def _get_model_response(model_name, model_obj):
    response_schema = model_obj.response_schema

    if response_schema is not None:
        return response_schema

    return responses.Prediction


router = fastapi.APIRouter(prefix="/models")


def _save_uploaded_files(kwargs):
    """Store uploaded files on disk and pass them to the model as UploadedFile.

    Models expect to receive uploaded files as
    :py:class:`deepaas.model.v2.wrapper.UploadedFile` objects, whose
    ``filename`` attribute points to a file in the local filesystem, so we
    store every upload in a temporary file.

    :returns: a tuple with the new arguments and the list of temporary files
        created, that have to be removed once the request has been served.
    """
    tmp_files = []
    new_kwargs = {}
    for key, val in kwargs.items():
        if isinstance(val, starlette.datastructures.UploadFile):
            # Keep the extension, so that the file type can be guessed
            suffix = os.path.splitext(val.filename or "")[1]
            fd, name = tempfile.mkstemp(suffix=suffix)
            tmp_files.append(name)
            with os.fdopen(fd, "w+b") as f:
                val.file.seek(0)
                shutil.copyfileobj(val.file, f)
            val = model.v2.wrapper.UploadedFile(
                name=key,
                filename=name,
                content_type=val.content_type,
                original_filename=val.filename,
            )
        new_kwargs[key] = val
    return new_kwargs, tmp_files


JSON_MEDIA_TYPES = ("application/json", "*/*")


def _get_accept_choices(accept_field):
    """Get the media types that the model can produce, and the default one.

    Models can declare an ``accept`` argument whose value is taken from the
    ``Accept`` HTTP header of the request, as in DEEPaaS v2.

    :returns: a tuple ``(choices, default)``.
    """
    choices = []
    validators = accept_field.validate
    if validators is not None:
        if not isinstance(validators, (list, tuple)):
            validators = [validators]
        for v in validators:
            choices.extend(getattr(v, "choices", []))

    default = accept_field.load_default
    if default is marshmallow.missing or default is None:
        default = choices[0] if choices else "application/json"
    return choices, default


def _negotiate_accept(header, choices, default):
    """Choose the media type that the model will produce.

    :param header: value of the ``Accept`` header of the request.
    :param choices: media types the model can produce (empty means any).
    :param default: media type to use if the client accepts any.
    :raises fastapi.HTTPException: if no acceptable media type is found.
    """
    if not header:
        return default

    accepted = [m.split(";")[0].strip() for m in header.split(",")]
    accepted = [m for m in accepted if m]
    for media_type in accepted:
        if media_type == "*/*":
            return default
        if not choices or media_type in choices:
            return media_type

    raise fastapi.HTTPException(
        status_code=406,
        detail=f"Not acceptable, supported media types are: {', '.join(choices)}",
    )


def _get_media_type(accept, filename=None):
    """Get a concrete media type for a response.

    If the requested type contains wildcards (e.g. ``image/*``) we try to guess
    the real one from the returned file name.
    """
    if "*" in accept:
        guessed = mimetypes.guess_type(filename)[0] if filename else None
        return guessed or "application/octet-stream"
    return accept


def _remove_files(files):
    """Remove the given files, ignoring the ones that do not exist."""
    for f in files:
        try:
            os.remove(f)
        except FileNotFoundError:
            pass
        except OSError as e:
            LOG.warning("Could not remove temporary file %s: %s", f, e)


def _get_handler_for_model(model_name, model_obj):
    """Auxiliary function to get the handler for a model.

    This function returns a handler for a model that can be used to
    register the routes in the router.

    """

    user_declared_args = dict(model_obj.get_predict_args())

    # NOTE(aloga): the "accept" argument is special, as in v2 it is taken from
    # the Accept header of the request, not from the request parameters.
    accept_field = user_declared_args.pop("accept", None)
    if accept_field is not None:
        accept_choices, accept_default = _get_accept_choices(accept_field)
    else:
        accept_choices, accept_default = [], "application/json"

    pydantic_schema = utils.get_pydantic_schema_from_marshmallow_fields(
        "PydanticSchema",
        user_declared_args,
    )

    class Handler(object):
        """Class to handle the model metadata endpoints."""

        model_name = None
        model_obj = None

        def __init__(self, model_name, model_obj):
            self.model_name = model_name
            self.model_obj = model_obj

        async def predict(
            self,
            request: fastapi.Request,
            args: pydantic_schema = fastapi.Depends(),  # noqa(B008)
        ):
            """Make a prediction given the input data."""

            kwargs = args.model_dump(by_alias=True)
            accept = "application/json"
            if accept_field is not None:
                accept = _negotiate_accept(
                    request.headers.get("accept"), accept_choices, accept_default
                )
                kwargs["accept"] = accept

            kwargs, tmp_files = _save_uploaded_files(kwargs)
            # Temporary files are removed once the response has been sent, as
            # the model may return one of them (e.g. the uploaded image).
            cleanup = starlette.background.BackgroundTask(_remove_files, tmp_files)

            try:
                ret = await self.model_obj.predict(**kwargs)

                if isinstance(ret, model.v2.wrapper.ReturnedFile):
                    return fastapi.responses.FileResponse(
                        ret.filename,
                        media_type=_get_media_type(accept, ret.filename),
                        background=cleanup,
                    )

                if accept not in JSON_MEDIA_TYPES:
                    if isinstance(ret, io.IOBase):
                        with ret:
                            ret = ret.read()
                    return fastapi.responses.Response(
                        content=ret,
                        media_type=_get_media_type(accept),
                        background=cleanup,
                    )

                if self.model_obj.has_schema:
                    # FIXME(aloga): Validation does not work, as we are converting
                    # from Marshmallow to Pydantic, check this as son as possible.
                    # self.model_obj.validate_response(ret)
                    return fastapi.responses.JSONResponse(
                        content=ret, background=cleanup
                    )

                return fastapi.responses.JSONResponse(
                    content={"status": "OK", "predictions": ret},
                    background=cleanup,
                )
            except BaseException:
                _remove_files(tmp_files)
                raise

        def register_routes(self, router):
            """Register the routes in the router."""

            response = _get_model_response(self.model_name, self.model_obj)

            # Document the media types that the model can produce, so that
            # clients (e.g. Swagger UI) can choose them via the Accept header.
            extra_responses = {}
            other_types = [m for m in accept_choices if m not in JSON_MEDIA_TYPES]
            if other_types:
                extra_responses = {
                    200: {"content": {m: {} for m in other_types}},
                    406: {"description": "Requested media type not supported"},
                }

            router.add_api_route(
                f"/{self.model_name}/predict",
                self.predict,
                methods=["POST"],
                response_model=response,
                responses=extra_responses,
                tags=["models", "predict"],
            )

    return Handler(model_name, model_obj)


def get_router():
    """Auxiliary function to get the router.

    We use this function to be able to include the router in the main
    application and do things before it gets included.

    In this case we explicitly include the model precit endpoint.

    """
    model_name = model.V2_MODEL_NAME
    model_obj = model.V2_MODEL

    hdlr = _get_handler_for_model(model_name, model_obj)
    hdlr.register_routes(router)

    return router
