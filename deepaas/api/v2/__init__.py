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


import flask
import flask_restplus

from deepaas.api.v2 import models as v2_model
from deepaas.api.v2 import predict as v2_predict
from deepaas.api.v2 import train as v2_train
from deepaas import model

# Get the models (this is a singleton, so it is safe to call it multiple times
model.register_models()

ns = flask_restplus.Namespace(
    'models',
    description='Model information, inference and training operations')


def get_blueprint(doc="/", add_specs=True):
    bp = flask.Blueprint('v2', __name__, url_prefix="/v2")

    api = flask_restplus.Api(
        bp,
        version="2.0.0",
        title='DEEP as a Service API V2 endpoint',
        description='DEEP as a Service (DEEPaaS) API endpoint.',
        doc=doc,
        add_specs=add_specs,
    )
    api.add_namespace(ns)
    api.add_namespace(v2_model.ns)
    api.add_namespace(v2_predict.ns)
    api.add_namespace(v2_train.ns)

    return bp
