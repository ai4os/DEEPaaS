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

from oslo_log import log
from webargs import fields
from webargs import validate

from deepaas.model.v2 import base

LOG = log.getLogger(__name__)


class TestModel(base.BaseModel):
    """Dummy model implementing minimal functionality.

    This is a simple class that mimics the behaviour of a module, just for
    showing how the whole DEEPaaS works and documentation purposes.
    """

    name = "deepaas-test"

    # FIXME(aloga): document this
    schema = {
        "date": fields.Date(),
        "labels": fields.List(
            fields.Nested(
                {
                    "label": fields.Str(),
                    "probability": fields.Float(),
                },
            )
        ),
    }

    def warm(self):
        LOG.debug("Test model is warming...")

    def predict(self, **kwargs):
        LOG.debug("Got the following kw arguments: %s", kwargs)
        return {
            "date": "2019-01-1",
            "labels": [{"label": "foo", "probability": 1.0}]
        }

    def train(self, *args, **kwargs):
        LOG.debug("Got the following arguments: %s", args)
        LOG.debug("Got the following kw arguments: %s", kwargs)

    def get_predict_args(self):
        return {
            "data": fields.Field(
                description="Data file to perform inference.",
                required=True,
                location="form",
                type="file",
            ),
            "parameter": fields.Int(
                description="This is a parameter for prediction",
                required=True
            ),
            "parameter_three": fields.Str(
                description=("This is a parameter that forces its value to "
                             "be one of the choices declared in 'enum'"),
                enum=["foo", "bar"],
                validate=validate.OneOf(["foo", "bar"]),
            )
        }

    def get_train_args(self):
        return {
            "parameter_one": fields.Int(
                required=True,
                descripton='This is a integer parameter, and it is '
                           'a required one.'
            ),
            "parameter_two": fields.Str(
                description='This is a string parameter.'
            ),
        }

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
            "url": "https://github.com/indigo-dc/DEEPaaS/",
            "license": "Apache 2.0",
        }
        return d
