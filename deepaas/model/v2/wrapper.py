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

from aiohttp import web
import marshmallow

from oslo_log import log

LOG = log.getLogger(__name__)


def catch_error(f):
    """Decorator to catch errors when executing the underlying methods."""

    def wrap(*args, **kwargs):
        name = args[0].name
        try:
            return f(*args, **kwargs)
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
            LOG.error("An exception has happened when calling '%s' method on "
                      "'%s' model." % (f, name))
            LOG.exception(e)
            if isinstance(e, web.HTTPException):
                raise e
            else:
                raise web.HTTPInternalServerError(reason=e)
    return wrap


class ModelWrapper(object):
    """Class that will wrap the loaded models before exposing them.

    Whenever a model is loaded it will be wrapped with this class to create a
    wrapper object that will handle the calls to the model's methods so as to
    handle non-existent method exceptions.

    :param name: Model name
    :param model: Model object
    :raises HTTPInternalServerError: in case that a model has defined
        a reponse schema that is nod JSON schema valid (DRAFT 4)
    """
    def __init__(self, name, model_obj):
        self.name = name
        self.model_obj = model_obj

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

    def validate_response(self, response):
        """Validate a response against the model's response schema, if set.

        If the wrapped model has defined a ``response`` attribute we will
        validate the response that

        :param response: The reponse that will be validated.
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

    @catch_error
    def predict(self, **kwargs):
        """Perform a prediction on wrapped model's ``predict`` method.

        :raises HTTPNotImplemented: If the method is not
            implemented in the wrapper model.
        :raises HTTPInternalServerError: If the call produces
            an error
        :raises HTTPException: If the call produces an
            error, already wrapped as a HTTPException
        """
        return self.model_obj.predict(**kwargs)

    @catch_error
    def train(self, *args, **kwargs):
        """Perform a training on wrapped model's ``train`` method.

        :raises HTTPNotImplemented: If the method is not
            implemented in the wrapper model.
        :raises HTTPInternalServerError: If the call produces
            an error
        :raises HTTPException: If the call produces an
            error, already wrapped as a HTTPException
        """
        return self.model_obj.train(*args, **kwargs)

    @catch_error
    def get_train_args(self):
        """Add training arguments into the training parser.

        :param parser: an argparse like object

        This method will call the wrapped model ``add_training_args``. If the
        method does not exist, but the wrapped model implements the DEPRECATED
        ``get_train_args`` we will try to load the arguments from there.
        """
        try:
            return self.model_obj.get_train_args()
        except (NotImplementedError, AttributeError):
            return {}

    @catch_error
    def get_predict_args(self):
        """Add predict arguments into the predict parser.

        :param parser: an argparse like object

        This method will call the wrapped model ``add_predict_args``. If the
        method does not exist, but the wrapped model implements the DEPRECATED
        ``get_predict_args`` we will try to load the arguments from there.
        """
        try:
            return self.model_obj.get_predict_args()
        except (NotImplementedError, AttributeError):
            return {}
