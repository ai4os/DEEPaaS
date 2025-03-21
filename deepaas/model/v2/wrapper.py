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

import asyncio
import collections
import contextlib
import functools
import io
import os
import tempfile

from aiohttp import web
import marshmallow
from oslo_config import cfg

from deepaas.api.v2 import utils
from deepaas import log

LOG = log.getLogger(__name__)

CONF = cfg.CONF


UploadedFile = collections.namedtuple(
    "UploadedFile", ("name", "filename", "content_type", "original_filename")
)
"""Class to hold uploaded field metadata when passed to model's methods

.. py:attribute:: name

   Name of the argument where this file is being sent.

.. py:attribute:: filename

   Complete file path to the temporary file in the filesystem,

.. py:attribute:: content_type

   Content-type of the uploaded file

.. py:attribute:: original_filename

   Filename of the original file being uploaded.
"""

ReturnedFile = collections.namedtuple(
    "ReturnedFile", ("name", "filename", "content_type", "original_filename")
)
"""Class to pass the files returned from predict in a pickable way

.. py:attribute:: name

   Name of the argument where this file is being sent.

.. py:attribute:: filename

   Complete file path to the temporary file in the filesystem,

.. py:attribute:: content_type

   Content-type of the uploaded file

.. py:attribute:: original_filename

   Filename of the original file being uploaded.
"""


# set defaults to None, mainly for compatibility (vkoz)
UploadedFile.__new__.__defaults__ = (None, None, None, None)
ReturnedFile.__new__.__defaults__ = (None, None, None, None)


class ModelWrapper(object):
    """Class that will wrap the loaded models before exposing them.

    Whenever a model is loaded it will be wrapped with this class to create a
    wrapper object that will handle the calls to the model's methods so as to
    handle non-existent method exceptions.

    :param name: Model name
    :param model: Model object
    :raises HTTPInternalServerError: in case that a model has defined
        a response schema that is not JSON schema valid (DRAFT 4)
    """

    def __init__(self, name, model_obj):
        self.name = name
        self.model_obj = model_obj

        schema = getattr(self.model_obj, "schema", None)

        if isinstance(schema, dict):
            try:
                schema = marshmallow.Schema.from_dict(
                    schema, name="ModelPredictionResponse"
                )
                self.has_schema = True
            except Exception as e:
                LOG.exception(e)
                # FIXME(aloga): do not use web exception here
                raise web.HTTPInternalServerError(
                    reason=("Model defined schema is invalid, " "check server logs.")
                )
        elif schema is not None:
            try:
                if issubclass(schema, marshmallow.Schema):
                    self.has_schema = True
            except TypeError:
                # FIXME(aloga): do not use web exception here
                raise web.HTTPInternalServerError(
                    reason=("Model defined schema is invalid, " "check server logs.")
                )
        else:
            self.has_schema = False

        # Now convert to pydantic schema...
        # FIXME(aloga): use try except
        if schema is not None:
            self.response_schema = utils.pydantic_from_marshmallow(
                "ModelPredictionResponse", schema
            )
        else:
            self.response_schema = None

    @contextlib.contextmanager
    def _catch_error(self):
        name = self.name
        try:
            yield
        except AttributeError:
            raise web.HTTPNotImplemented(
                reason=("Not implemented by underlying model (loaded '%s')" % name)
            )
        except NotImplementedError:
            raise web.HTTPNotImplemented(
                reason=("Model '%s' does not implement this functionality" % name)
            )
        except Exception as e:
            LOG.error(
                "An exception has happened when calling method on " "'%s' model." % name
            )
            LOG.exception(e)
            if isinstance(e, web.HTTPException):
                raise e
            else:
                raise web.HTTPInternalServerError(reason=e)

    def validate_response(self, response):
        """Validate a response against the model's response schema, if set.

        If the wrapped model has defined a ``response`` attribute we will
        validate the response that

        :param response: The response that will be validated.
        :raises exceptions.InternalServerError: in case the reponse cannot be
            validated.
        """
        if self.has_schema is not True:
            raise web.HTTPInternalServerError(
                reason=(
                    "Trying to validate against a schema, but I do not "
                    "have one defined"
                )
            )

        try:
            self.response_schema().load(response)
        except marshmallow.ValidationError as e:
            LOG.exception(e)
            raise web.HTTPInternalServerError(
                reason="ERROR validating model response, check server logs."
            )
        except Exception as e:
            LOG.exception(e)
            raise web.HTTPInternalServerError(
                reason="Unknown ERROR validating response, check server logs."
            )

        return True

    def get_metadata(self):
        """Obtain model's metadata.

        If the model's metadata cannot be obtained because it is not
        implemented, we will provide some generic information so that the
        call does not fail.

        :returns dict: dictionary containing model's metadata
        """
        try:
            d = self.model_obj.get_metadata()
        except (NotImplementedError, AttributeError):
            d = {
                "id": "0",
                "name": self.name,
                "description": (
                    "Could not load description from "
                    "underlying model (loaded '%s')" % self.name
                ),
            }
        return d

    def _run_in_pool(self, func, *args, **kwargs):
        fn = functools.partial(func, *args, **kwargs)
        ret = self._loop.create_task(self._executor.apply(fn))
        return ret

    async def warm(self):
        """Warm (i.e. load, initialize) the underlying model.

        This method is called automatically when the model is loaded. You
        should use this method to initialize the model so that it is ready for
        the first prediction.

        The model receives no arguments.
        """
        try:
            func = self.model_obj.warm
        except AttributeError:
            LOG.debug("Cannot warm (initialize) model '%s'" % self.name)
            return

        try:
            n = self._workers
            LOG.debug("Warming '%s' model with %s workers" % (self.name, n))
            fs = [self._run_in_pool(func) for _ in range(0, n)]
            await asyncio.gather(*fs)
            LOG.debug("Model '%s' has been warmed" % self.name)
        except NotImplementedError:
            LOG.debug("Cannot warm (initialize) model '%s'" % self.name)

    @staticmethod
    def predict_wrap(predict_func, *args, **kwargs):
        """Wrapper function to allow returning files from predict
        This wrapper exists because buffer objects are not pickable,
        thus cannot be returned from the executor.
        """
        ret = predict_func(*args, **kwargs)
        if isinstance(ret, io.BufferedReader):
            ret = ReturnedFile(filename=ret.name)

        return ret

    async def predict(self, *args, **kwargs):
        """Perform a prediction on wrapped model's ``predict`` method.

        :raises HTTPNotImplemented: If the method is not
            implemented in the wrapper model.
        :raises HTTPInternalServerError: If the call produces
            an error
        :raises HTTPException: If the call produces an
            error, already wrapped as a HTTPException
        """
        for key, val in kwargs.items():
            if isinstance(val, web.FileField):
                fd, name = tempfile.mkstemp()
                fd = os.fdopen(fd, "w+b")
                fd.write(val.file.read())
                fd.close()
                aux = UploadedFile(
                    name=val.name,
                    filename=name,
                    content_type=val.content_type,
                    original_filename=val.filename,
                )
                kwargs[key] = aux
                # FIXME(aloga); cleanup of tmpfile here

        with self._catch_error():
            return self.predict_wrap(self.model_obj.predict, *args, **kwargs)

    def get_predict_args(self):
        """Add predict arguments into the predict parser.

        :param parser: an argparse like object

        This method will call the wrapped model ``get_predict_args``.
        """
        try:
            args = self.model_obj.get_predict_args()
        except (NotImplementedError, AttributeError):
            args = {}
        return args
