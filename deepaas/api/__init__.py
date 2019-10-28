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
import aiohttp_apispec
from oslo_config import cfg
from oslo_log import log as logging

import deepaas
from deepaas.api import v2
from deepaas.api import versions
from deepaas import model

LOG = logging.getLogger(__name__)

APP = None

CONF = cfg.CONF


def get_app(doc="/docs"):
    """Get the main app."""
    global APP

    if APP:
        return APP

    APP = web.Application(debug=CONF.debug)

    if CONF.enable_v1:
        LOG.warning("Using V1 version of the API is not anymore supported "
                    "and marked as deprecated, please switch to V2 as soon "
                    "as possible.")

        from deepaas.api import v1  # noqa

        model.register_v1_models()

        v1app = v1.get_app()
        APP.add_subapp("/v1", v1app)
        versions.register_version("deprecated", v1.get_version)

        LOG.info("Serving loaded V1 models: %s", list(model.V1_MODELS.keys()))

    model.register_v2_models()

    v2app = v2.get_app()
    APP.add_subapp("/v2", v2app)
    versions.register_version("stable", v2.get_version)

    APP.add_routes(versions.routes)

    LOG.info("Serving loaded V2 models: %s", list(model.V2_MODELS.keys()))

    if doc:
        # init docs with all parameters, usual for ApiSpec
        aiohttp_apispec.setup_aiohttp_apispec(
            app=APP,
            title="DEEP as a Service API endpoint",
            description="DEEP as a Service (DEEPaaS) API endpoint.",
            version=deepaas.__version__,
            url="/swagger.json",
            swagger_path=doc,
        )

    return APP
