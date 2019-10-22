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

import jsonschema
import jsonschema.exceptions
from oslo_log import log
import werkzeug.exceptions as exceptions

from deepaas.model import loading
from deepaas.model.v2 import test

LOG = log.getLogger(__name__)

# Model registry
MODELS = {}
MODELS_LOADED = False


def register_models():
    global MODELS
    global MODELS_LOADED

    if MODELS_LOADED:
        return

    try:
        for name, model in loading.get_available_models("v2").items():
            MODELS[name] = ModelWrapper(name, model)
    except Exception as e:
        LOG.warning("Error loading models: %s", e)

    if MODELS:
        MODELS_LOADED = True
        return

    LOG.warning("No models found using V2 namespace, trying with V1. This is "
                "DEPRECATED and it is done only to try to preserve backards "
                "compatibility, but may lead to unexpected behaviour. You "
                "should move to the new namespace as soon as possible. Please "
                "refer to the documentation to get more details.")

    try:
        for name, model in loading.get_available_models("v1").items():
            MODELS[name] = ModelWrapper(name, model)
    except Exception as e:
        LOG.warning("Error loading models: %s", e)

    if not MODELS:
        LOG.info("No models found with V2 or V1 namespace, loading test model")
        MODELS["deepaas-test"] = ModelWrapper("deepaas-test", test.TestModel())
    MODELS_LOADED = True


class ModelWrapper(object):
    """Class that will wrap the loaded models before exposing them.

    Whenever a model is loaded it will be wrapped with this class to create a
    wrapper object that will handle the calls to the model's methods so as to
    handle non-existent method exceptions.

    :param name: Model name
    :param model: Model object
    :raises exceptions.InternalServerError: in case that a model has defined
        a reponse schema that is nod JSON schema valid (DRAFT 4)
    """
    def __init__(self, name, model):
        self.name = name
        self.model = model

        schema = getattr(self.model, "response", None)

        if schema is not None:
            try:
                jsonschema.Draft4Validator.check_schema(schema)
            except jsonschema.exceptions.SchemaError as e:
                LOG.exception(e)
                raise exceptions.InternalServerError(
                    description="Model defined schema is invalid, "
                                "check server logs."
                )
            self.response_validator = jsonschema.Draft4Validator(schema)
            self.has_schema = True
        else:
            self.response_validator = None
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
            raise exceptions.InternalServerError(
                "Trying to validate against a schema, but I do not have one"
                "defined")

        try:
            self.response_validator.validate(response)
        except jsonschema.exceptions.ValidationError as e:
            LOG.exception(e)
            raise exceptions.InternalServerError(
                description="ERROR marshaling response, check server logs.")

    def _call_method(self, method, *args, **kwargs):
        try:
            meth = getattr(self.model, method)
            return meth(*args, **kwargs)
        except AttributeError:
            raise exceptions.NotImplemented("Not implemented by underlying "
                                            "model (loaded '%s')" % self.name)
        except NotImplementedError:
            raise exceptions.NotImplemented("Model '%s' does not implement "
                                            "this functionality" % self.name)
        except Exception as e:
            LOG.error("An exception has happened when calling '%s' method on "
                      "'%s' model." % (method, self.name))
            LOG.exception(e)
            if isinstance(e, exceptions.HTTPException):
                raise e
            else:
                raise exceptions.InternalServerError(description=e)

    def get_metadata(self):
        """Obtain model's metadata.

        If the model's metadata cannot be obtained because it is not
        implemented, we will provide some generic information so that the
        call does not fail.

        :returns dict: dictionary containing model's metadata
        """
        try:
            d = self.model.get_metadata()
        except (NotImplementedError, AttributeError):
            d = {
                "id": "0",
                "name": self.name,
                "description": ("Could not load description from "
                                "underlying model (loaded '%s')" % self.name),
            }
        return d

    @property
    def response(self):
        """Wrapped model's response schema.

        Check :py:attr:`deepaas.v2.base.BaseModel.response` for more details.
        """
        return getattr(self.model, "response", None)

    def predict(self, **kwargs):
        """Perform a prediction on wrapped model's ``predict`` method.

        :raises werkzeug.exceptions.NotImplemented: If the method is not
            implemented in the wrapper model.
        :raises werkzeug.exceptions.InternalServerError: If the call produces
            an error
        :raises werkzeug.exceptions.HTTPException: If the call produces an
            error, already wrapped as a werkzeug.exceptions.HTTPException
            method
        """
        return self._call_method("predict", **kwargs)

    def train(self, *args, **kwargs):
        """Perform a training on wrapped model's ``train`` method.

        :raises werkzeug.exceptions.NotImplemented: If the method is not
            implemented in the wrapper model.
        :raises werkzeug.exceptions.InternalServerError: If the call produces
            an error
        :raises werkzeug.exceptions.HTTPException: If the call produces an
            error, already wrapped as a werkzeug.exceptions.HTTPException
            method
        """
        return self._call_method("train", *args, **kwargs)

    def add_train_args(self, parser):
        """Add training arguments into the training parser.

        :param parser: an argparse like object

        This method will call the wrapped model ``add_training_args``. If the
        method does not exist, but the wrapped model implements the DEPRECATED
        ``get_train_args`` we will try to load the arguments from there.
        """
        try:
            return self._call_method("add_train_args", parser)
        except exceptions.NotImplemented:
            try:
                args = self._call_method("get_train_args")
                LOG.warning("Loading training arguments using the old and "
                            "DEPRECATED 'get_train_args' function. You should "
                            "move to the 'add_train_args' function as soon as"
                            "possible. This is only supported for backwards "
                            "compatibility and may lead to unexpected "
                            "behaviour.")
                for k, v in args.items():
                    parser.add_argument(k, **v)
                return parser
            except exceptions.NotImplemented:
                return parser

    def add_predict_args(self, parser):
        """Add predict arguments into the predict parser.

        :param parser: an argparse like object

        This method will call the wrapped model ``add_predict_args``. If the
        method does not exist, but the wrapped model implements the DEPRECATED
        ``get_predict_args`` we will try to load the arguments from there.
        """
        try:
            return self._call_method("add_predict_args", parser)
        except exceptions.NotImplemented:
            try:
                args = self._call_method("get_test_args")
                LOG.warning("Loading predict arguments using the old and "
                            "DEPRECATED 'get_test_args' function. You should "
                            "move to the 'add_predict_args' function as soon "
                            "as possible. This is only supported for "
                            "backwards compatibility and may lead to "
                            "unexpected behaviour.")
                for k, v in args.items():
                    parser.add_argument(k, **v)
                return parser
            except exceptions.NotImplemented:
                return parser
