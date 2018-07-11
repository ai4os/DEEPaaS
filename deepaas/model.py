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

import werkzeug.exceptions as exceptions

from deepaas import loading


class BaseModel(object):
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
            d = self._get_method("get_metadata")
        except exceptions.NotImplemented:
            d = {
                "id": "0",
                "name": self.name,
                "description": ("Could not load description from "
                                "underlying model (loaded '%s')" % self.name),
            }
        return d

    def predict_file(self, *args):
        return self._get_method("predict_file")(*args)

    def predict_data(self, *args):
        return self._get_method("predict_data")(*args)

    def predict_url(self, *args):
        return self._get_method("predict_url")(*args)

    def train(self, *args):
        return self._get_method("train", *args)


class TestModel(BaseModel):
    def __init__(self, name):
        super(TestModel, self).__init__(name, None)

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


def populate_models():
    models = {}
    try:
        for name, model in loading.get_available_models().items():
            models[name] = BaseModel(name, model)
    except Exception as e:
        # TODO(aloga): use logging, not prints
        print("Cannot load any models: %s" % e)
    if not models:
        print("Loading test model")
        models["deepaas-test"] = TestModel("deepaas-test")
    return models

MODELS = populate_models()
