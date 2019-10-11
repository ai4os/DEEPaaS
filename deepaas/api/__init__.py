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
from oslo_log import log as logging

from deepaas.api import v1
from deepaas import model

LOG = logging.getLogger(__name__)

APP = None


def get_app(doc="/", add_specs=True):
    """Get the Flask-RESTPlus app.

    Set doc to False if you do not want to get the Swagger documentation.
    Set add_spces to False if you do not want to generate the swagger.json
    specs file
    """
    global APP

    if APP:
        return APP

    model.register_models()

    APP = flask.Flask(__name__)

    for api in (v1, ):
        bp = getattr(api, "get_blueprint")(doc=doc, add_specs=add_specs)
        APP.register_blueprint(bp)

    APP.config.SWAGGER_UI_DOC_EXPANSION = 'list'

    LOG.info("Serving loaded models: %s", model.MODELS.keys())

    return APP
