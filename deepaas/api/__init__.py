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
from oslo_log import log as logging

import deepaas
from deepaas.api import v1
from deepaas import model

LOG = logging.getLogger(__name__)

APP = None


def get_app(doc="/"):
    """Get the Flask-RESTPlus app.

    Set doc to False if you do not want to get the Swagger documentation.
    """
    global APP

    if APP:
        return APP

    model.register_models()

    APP = flask.Flask(__name__)
    APP.config.SWAGGER_UI_DOC_EXPANSION = 'list'

    print(doc)
    api = flask_restplus.Api(
        APP,
        version=deepaas.__version__,
        title='DEEP as a Service API endpoint',
        description='DEEP as a Service (DEEPaaS) API endpoint.',
        doc=doc
    )

    api.add_namespace(v1.api, path="/models")

    LOG.info("Serving loaded models: %s", model.MODELS.keys())

    return APP
