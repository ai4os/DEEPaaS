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

import json

import fastapi
import fastapi.responses
from oslo_config import cfg

import deepaas
from deepaas.api import v2
from deepaas import log
from deepaas import model

LOG = log.getLogger(__name__)

APP = None
VERSIONS = {}

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


def get_fastapi_app(
    enable_doc: bool = True,
    enable_train: bool = True,  # FIXME(aloga): not handled yet
    enable_predict: bool = True,  # FIXME(aloga): not handled yet
    base_path: str = "",
) -> fastapi.FastAPI:
    """Get the main app, based on FastAPI."""
    global APP
    global VERSIONS

    if APP:
        return APP

    APP = fastapi.FastAPI(
        title="DEEP as a Service API endpoint",
        description=API_DESCRIPTION,
        version=deepaas.extract_version(),
        docs_url=f"{base_path}/docs" if enable_doc else None,  # NOTE(aloga): changed
        redoc_url=f"{base_path}/redoc" if enable_doc else None,  # NOTE(aloga): new
        openapi_url=f"{base_path}/openapi.json",  # NOTE(aloga): changed
    )

    model.load_v2_model()
    LOG.info("Serving loaded V2 model: %s", model.V2_MODEL_NAME)

    if CONF.warm:
        LOG.debug("Warming models...")
        model.V2_MODEL.warm()

    v2app = v2.get_app(
        # FIXME(aloga): these have no effect now, remove.
        enable_train=enable_train,
        enable_predict=enable_predict,
    )

    APP.include_router(v2app, prefix=f"{base_path}/v2", tags=["v2"])
    VERSIONS["v2"] = v2.get_v2_version

    APP.add_api_route(
        f"{base_path}/",
        get_root,
        methods=["GET"],
        summary="Get API version information",
        tags=["version"],
    )

    return APP


async def get_root(request: fastapi.Request) -> fastapi.responses.JSONResponse:
    versions = []
    for _ver, info in VERSIONS.items():
        resp = await info(request)
        versions.append(json.loads(resp.body))

    root = str(request.url_for("get_root"))

    response = {"versions": versions, "links": []}

    doc = APP.docs_url.strip("/")
    if doc:
        doc = {"rel": "help", "type": "text/html", "href": f"{root}{doc}"}
        response["links"].append(doc)

    redoc = APP.redoc_url.strip("/")
    if redoc:
        redoc = {"rel": "help", "type": "text/html", "href": f"{root}{redoc}"}
        response["links"].append(redoc)

    spec = APP.openapi_url.strip("/")
    if spec:
        spec = {
            "rel": "describedby",
            "type": "application/json",
            "href": f"{root}{spec}",
        }
        response["links"].append(spec)

    return fastapi.responses.JSONResponse(content=response)


# FIXME(aloga): kept here as a reference, remove when aiohttp is removed
# async def get_aiohttp_app(
#     swagger=True,
#     enable_doc=True,
#     doc="/api",
#     prefix="",
#     static_path="/static/swagger",
#     base_path="",
#     enable_train=True,
#     enable_predict=True,
# ):
#     """Get the main app, based on aiohttp."""
#     global APP

#     if APP:
#         return APP

#     APP = web.Application(debug=CONF.debug, client_max_size=CONF.client_max_size)

#     APP.middlewares.append(web.normalize_path_middleware())

#     model.register_v2_models(APP)

#     v2app = v2.get_app(enable_train=enable_train, enable_predict=enable_predict)
#     if base_path:
#         path = str(pathlib.Path(base_path) / "v2")
#     else:
#         path = "/v2"
#     APP.add_subapp(path, v2app)
#     versions.register_version("stable", v2.get_version)

#     if base_path:
#         # Get versions.routes, and transform them to have the base_path, as we cannot
#         # directly modify the routes already created and stored in the RouteTableDef
#         for route in versions.routes:
#             APP.router.add_route(
#                 route.method, str(pathlib.Path(base_path + route.path)), route.handler
#             )
#     else:
#         APP.add_routes(versions.routes)

#     LOG.info("Serving loaded V2 models: %s", list(model.V2_MODELS.keys()))

#     if CONF.warm:
#         for _, m in model.V2_MODELS.items():
#             LOG.debug("Warming models...")
#             await m.warm()

#     if swagger:
#         doc = str(pathlib.Path(base_path + doc))
#         swagger = str(pathlib.Path(base_path + "/swagger.json"))
#         static_path = str(pathlib.Path(base_path + static_path))

#         # init docs with all parameters, usual for ApiSpec
#         aiohttp_apispec.setup_aiohttp_apispec(
#             app=APP,
#             title="DEEP as a Service API endpoint",
#             info={
#                 "description": API_DESCRIPTION,
#             },
#             externalDocs={
#                 "description": "API documentation",
#                 "url": "https://deepaas.readthedocs.org/",
#             },
#             version=deepaas.extract_version(),
#             url=swagger,
#             swagger_path=doc if enable_doc else None,
#             prefix=prefix,
#             static_path=static_path,
#             in_place=True,
#         )
