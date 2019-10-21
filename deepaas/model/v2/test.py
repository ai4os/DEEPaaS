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
import werkzeug

from deepaas.model.v2 import base

LOG = log.getLogger(__name__)


class TestModel(base.BaseModel):
    """Dummy model implementing minimal functionality.

    This is a simple class that mimics the behaviour of a module, just for
    showing how the whole DEEPaaS works and documentation purposes.
    """

    name = "deepaas-test"

    response = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "type": "object",
        "properties": {
            "date": {"type": "string", "format": "date-time"},
            "labels": {
                "type": "array",
                "items": {"$ref": "#/definitions/Label"},
            },
        },
        "required": ["labels"],
        "definitions": {
            "Label": {
                "properties": {
                    "label": {"type": "string"},
                    "probability": {"type": "number"},
                },
                "required": ["label", "probability"],
                "type": "object",
            },
        },
    }

    def predict(self, **kwargs):
        LOG.debug("Got the following kw arguments: %s", kwargs)
        return {
            "date": "2019-01-1",
            "labels": [{"label": "foo", "probability": 1.0}]
        }

    def train(self, *args, **kwargs):
        LOG.debug("Got the following arguments: %s", args)
        LOG.debug("Got the following kw arguments: %s", kwargs)

    def add_predict_args(self, parser):
        # FIXME(aloga): currently we allow only to upload one file. There is a
        # bug in the Swagger UI that makes impossible to upload several files,
        # although this works if the request is not done through swagger. Since
        # providing a UI and an API that behave differently is incoherent, only
        # allow one file for the time being.
        #
        # See https://github.com/noirbizarre/flask-restplus/issues/491 for more
        # details on the bug.
        parser.add_argument('data',
                            help="Data file to perform inference.",
                            type=werkzeug.FileStorage,
                            location="files",
                            dest='files',
                            required=True)
        parser.add_argument("parameter",
                            type=int,
                            required=True,
                            help="This is a parameter for prediction.")
        return parser

    def add_train_args(self, parser):
        parser.add_argument('parameter_one',
                            type=int,
                            required=True,
                            help='This is a integer parameter, and it is '
                                 'a required one.')
        parser.add_argument('parameter_two',
                            type=str,
                            help='This is a string parameter.')
        return parser

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
