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

import os
import shutil
import tempfile

import fastapi
import fastapi.encoders
import fastapi.exceptions
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
            fd, name = tempfile.mkstemp()
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

    user_declared_args = model_obj.get_predict_args()
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
            self, args: pydantic_schema = fastapi.Depends()  # noqa(B008)
        ):
            """Make a prediction given the input data."""

            kwargs, tmp_files = _save_uploaded_files(args.model_dump(by_alias=True))
            # Temporary files are removed once the response has been sent, as
            # the model may return one of them (e.g. the uploaded image).
            cleanup = starlette.background.BackgroundTask(_remove_files, tmp_files)

            try:
                ret = await self.model_obj.predict(**kwargs)

                if isinstance(ret, model.v2.wrapper.ReturnedFile):
                    ret = open(ret.filename, "rb")

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

            router.add_api_route(
                f"/{self.model_name}/predict",
                self.predict,
                methods=["POST"],
                response_model=response,
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
