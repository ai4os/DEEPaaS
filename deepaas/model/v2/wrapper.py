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
from oslo_log import log
from webargs import fields

from deepaas.model.v2 import executor

LOG = log.getLogger(__name__)

CONF = cfg.CONF


UploadedFile = collections.namedtuple("UploadedFile", ("name",
                                                       "filename",
                                                       "content_type",
                                                       "original_filename"))
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

ReturnedFile = collections.namedtuple("ReturnedFile", ("name",
                                                       "filename",
                                                       "content_type",
                                                       "original_filename"))
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
    def __init__(self, name, model_obj, app=None):
        self.name = name
        self.model_obj = model_obj
        self._app = app

        self._loop = asyncio.get_event_loop()

        self._executor = self._init_executor()

        if self._app is not None:
            self._setup_cleanup()

        schema = getattr(self.model_obj, "schema", None)

        if isinstance(schema, dict):
            try:
                schema = marshmallow.Schema.from_dict(
                    schema,
                    name="ModelPredictionResponse"
                )
                self.has_schema = True
            except Exception as e:
                LOG.exception(e)
                raise web.HTTPInternalServerError(
                    reason=("Model defined schema is invalid, "
                            "check server logs.")
                )
        elif schema is not None:
            try:
                if issubclass(schema, marshmallow.Schema):
                    self.has_schema = True
            except TypeError:
                raise web.HTTPInternalServerError(
                    reason=("Model defined schema is invalid, "
                            "check server logs.")
                )
        else:
            self.has_schema = False

        self.response_schema = schema

    def _setup_cleanup(self):
        self._app.on_cleanup.append(self._close_executors)

    async def _close_executors(self, app):
        self._executor.shutdown()

    def _init_executor(self):
# FIXME(aloga): we need to implement worker number of threads, etc.
#        n = self._train_workers
        _executor = executor.get_default_executor()
        return _executor

    @contextlib.contextmanager
    def _catch_error(self):
        name = self.name
        try:
            yield
        except AttributeError:
            raise web.HTTPNotImplemented(
                reason=("Not implemented by underlying model (loaded '%s')" %
                        name)
            )
        except NotImplementedError:
            raise web.HTTPNotImplemented(
                reason=("Model '%s' does not implement this functionality" %
                        name)
            )
        except Exception as e:
            LOG.error("An exception has happened when calling method on "
                      "'%s' model." % name)
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
                reason=("Trying to validate against a schema, but I do not "
                        "have one defined")
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
                "description": ("Could not load description from "
                                "underlying model (loaded '%s')" % self.name),
            }
        return d

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

#        run = self._loop.run_in_executor
#        executor = self._predict_executor
#        n = self._predict_workers
#        try:
#            LOG.debug("Warming '%s' model with %s workers" % (self.name, n))
#            fs = [run(executor, func) for i in range(0, n)]
#            await asyncio.gather(*fs)
#            LOG.debug("Model '%s' has been warmed" % self.name)
#        except NotImplementedError:
#            LOG.debug("Cannot warm (initialize) model '%s'" % self.name)

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

    def predict(self, *args, **kwargs):
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
                    original_filename=val.filename
                )
                kwargs[key] = aux
                # FIXME(aloga); cleanup of tmpfile here

        with self._catch_error():
            ret = self._executor.submit(
                self.predict_wrap, self.model_obj.predict, *args, **kwargs
            )
            return ret

    def train(self, *args, **kwargs):
        """Perform a training on wrapped model's ``train`` method.

        :raises HTTPNotImplemented: If the method is not
            implemented in the wrapper model.
        :raises HTTPInternalServerError: If the call produces
            an error
        :raises HTTPException: If the call produces an
            error, already wrapped as a HTTPException
        """

        with self._catch_error():
            return self._executor.submit(
                self.model_obj.train, *args, **kwargs
            )

    def get_train_args(self):
        """Add training arguments into the training parser.

        :param parser: an argparse like object

        This method will call the wrapped model ``add_train_args``.
        """
        try:
            args = self.model_obj.get_train_args()
        except (NotImplementedError, AttributeError):
            args = {}
        return args

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

    def _convert_old_args(self, args):
        aux = {}
        for k, v in args.items():
            if isinstance(v, dict):
                LOG.warning("Loading arguments using the old and DEPRECATED "
                            "return value (i.e. an plain Python dictionary. "
                            "You should move to the new return value (i.e. a "
                            "webargs.fields dictionary as soon as possible. "
                            "All the loaded arguments will be converted to "
                            "strings. This is only supported for backwards "
                            "compatibility and may lead to unexpected errors. "
                            "Argument raising this warningr: '%s'", k)

                v = fields.Str(
                    missing=v.get("default"),
                    description=v.get("help"),
                    required=v.get("required"),
                )
            aux[k] = v
        return aux
