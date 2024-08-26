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

import pathlib

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

LINKS = """
- [Project website](https://deep-hybrid.datacloud.eu).
- [Project documentation](https://docs.deep-hybrid.datacloud.eu).
- [Model marketplace](https://marketplace.deep-hybrid.datacloud.eu).
"""

API_DESCRIPTION = (
    "<img"
    " src='https://marketplace.deep-hybrid-datacloud.eu/images/logo-deep.png'"
    " width=200 alt='' />"
    "\n\nThis is a REST API that is focused on providing access "
    "to machine learning models. By using the DEEPaaS API "
    "users can easily run a REST API in front of their model, "
    "thus accessing its functionality via HTTP calls. "
    "\n\nCurrently you are browsing the "
    "[Swagger UI](https://swagger.io/tools/swagger-ui/) "
    "for this API, a tool that allows you to visualize and interact with the "
    "API and the underlying model."
) + LINKS


async def get_app(
    swagger=True,
    enable_doc=True,
    doc="/api",
    prefix="",
    static_path="/static/swagger",
    base_path="",
    enable_train=True,
    enable_predict=True,
):
    """Get the main app."""
    global APP

    if APP:
        return APP

    APP = web.Application(debug=CONF.debug, client_max_size=CONF.client_max_size)

    APP.middlewares.append(web.normalize_path_middleware())

    model.register_v2_models(APP)

    v2app = v2.get_app(enable_train=enable_train, enable_predict=enable_predict)
    if base_path:
        path = str(pathlib.Path(base_path) / "v2")
    else:
        path = "/v2"
    APP.add_subapp(path, v2app)
    versions.register_version("stable", v2.get_version)

    if base_path:
        # Get versions.routes, and transform them to have the base_path, as we cannot
        # directly modify the routes already created and stored in the RouteTableDef
        for route in versions.routes:
            APP.router.add_route(
                route.method, str(pathlib.Path(base_path + route.path)), route.handler
            )
    else:
        APP.add_routes(versions.routes)

    LOG.info("Serving loaded V2 models: %s", list(model.V2_MODELS.keys()))

    if CONF.warm:
        for _, m in model.V2_MODELS.items():
            LOG.debug("Warming models...")
            await m.warm()

    if swagger:
        doc = str(pathlib.Path(base_path + doc))
        swagger = str(pathlib.Path(base_path + "/swagger.json"))
        static_path = str(pathlib.Path(base_path + static_path))

        # init docs with all parameters, usual for ApiSpec
        aiohttp_apispec.setup_aiohttp_apispec(
            app=APP,
            title="DEEP as a Service API endpoint",
            info={
                "description": API_DESCRIPTION,
            },
            externalDocs={
                "description": "API documentation",
                "url": "https://deepaas.readthedocs.org/",
            },
            version=deepaas.extract_version(),
            url=swagger,
            swagger_path=doc if enable_doc else None,
            prefix=prefix,
            static_path=static_path,
            in_place=True,
        )

    return APP
