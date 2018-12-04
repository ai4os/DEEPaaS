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

import abc

from oslo_log import log
import six
import werkzeug.exceptions as exceptions

from deepaas import loading

LOG = log.getLogger(__name__)

# Model registry
MODELS = {}
MODELS_LOADED = False


def register_models():
    global MODELS
    global MODELS_LOADED

    if MODELS_LOADED:
        return

    MODELS = {}
    try:
        for name, model in loading.get_available_models().items():
            MODELS[name] = ModelWrapper(name, model)
    except Exception as e:
        LOG.warning("Error loading models: %s", e)

    if not MODELS:
        LOG.info("No models found, loading test model")
        MODELS["deepaas-test"] = ModelWrapper("deepaas-test", TestModel())
    MODELS_LOADED = True


@six.add_metaclass(abc.ABCMeta)
class BaseModel(object):
    """Base class for all models to be used with DEEPaaS.

    Note that it is not needed for DEEPaaS to inherit from this abstract base
    class in order to expose the model functionality, but the entrypoint that
    is configured should expose the same API.
    """

    @abc.abstractmethod
    def predict_file(self, path, **kwargs):
        """Perform a prediction from a file in the local filesystem.

        This method will perform a prediction based on a file stored in the
        local filesystem.

        :param str path: path to the file to be analized
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def predict_data(self, data, **kwargs):
        """Perform a prediction from the data passed in the arguments.

        This method will use the raw data that is passed in the `data` argument
        to perfom the prediction.

        :param data: raw data to be analized
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def predict_url(self, *args):
        """Perform a predction from a remote URL.

        This method will perform a prediction based on the data stored in the
        URL passed as argument.

        :param str url: URL pointing to the data to be analized
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def get_metadata(self):
        """Return metadata from the eposed model.

        :return: dictionary containing the model's metadata.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def train(self, *args):
        """TBD."""
        raise NotImplementedError()

    @abc.abstractmethod
    def get_train_args(self, *args):
        """TBD."""
        raise NotImplementedError()


class TestModel(BaseModel):
    """Dummy model implementing minimal functionality.

    This is a simple class that mimics the behaviour of a module, just for
    showing how the whole DEEPaaS works and documentation purposes.
    """
    name = "deepaas-test"

    def predict_file(self, path, **kwargs):
        return super(TestModel, self).predict_file(path, **kwargs)

    def predict_data(self, data, **kwargs):
        return super(TestModel, self).predict_data(data, **kwargs)

    def predict_url(self, url, **kwargs):
        return super(TestModel, self).predict_url(url, **kwargs)

    def train(self, *args):
        return super(TestModel, self).train(*args)

    def get_train_args(self, *args):
        return {}

    def get_metadata(self):
        d = {
            "id": "0",
            "name": "deepaas-test",
            "description": ("This is not a model at all, just a placeholder "
                            "for testing the API functionality. If you are "
                            "seeing this, it is because DEEPaaS could not "
                            "load a valid model."),
            "author": "Alvaro Lopez Garcia",
            "version": "0.0.1",
        }
        return d


def catch_error(f):
    def wrap(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except NotImplementedError:
            raise exceptions.NotImplemented("Model does not implement "
                                            "this functionality")
    return wrap


class ModelWrapper(object):
    """Class that will wrap the loaded models before exposing them.

    Whenever we load a model with stevedore, we will use this class to create a
    wrapper object that will handle the calls to the model's methods so as to
    handle non-existent method exceptions.
    """
    def __init__(self, name, model):
        self.name = name
        self.model = model

    def _get_method(self, method):
        try:
            meth = getattr(self.model, method)
        except AttributeError:
            raise exceptions.NotImplemented(
                "Not implemented by underlying model (loaded '%s')" % self.name
            )
        return meth

    def get_metadata(self):
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

    @catch_error
    def predict_file(self, *args):
        return self._get_method("predict_file")(*args)

    @catch_error
    def predict_data(self, *args):
        return self._get_method("predict_data")(*args)

    @catch_error
    def predict_url(self, *args):
        return self._get_method("predict_url")(*args)

    @catch_error
    def train(self, *args):
        return self._get_method("train")(*args)

    @catch_error
    def get_train_args(self, *args):
        try:
            return self._get_method("get_train_args")(*args)
        except exceptions.NotImplemented:
            return {}
