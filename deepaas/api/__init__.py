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
from deepaas.api.v2 import responses
from deepaas import log
from deepaas import model

LOG = log.getLogger(__name__)

APP = None
VERSIONS = {}

CONF = cfg.CONF

LINKS = """
- [AI4EOSC Project website](https://ai4eosc.eu).
- [Project documentation](https://docs.ai4eosc.eu).
- [API documentation](https://docs.ai4os.eu/deepaas).
- [AI4EOSC Model marketplace](https://dashboard.cloud.ai4eosc.eu/marketplace).
"""

API_DESCRIPTION = (
    "<img"
    " src='https://raw.githubusercontent.com/ai4os/.github/ai4os/profile/"
    "horizontal-transparent.png'"
    " width=200 alt='' />"
    "\n\nThis is a REST API that is focused on providing access "
    "to machine learning models. "
    "\n\nCurrently you are browsing the "
    "[Swagger UI](https://swagger.io/tools/swagger-ui/) "
    "for this API, a tool that allows you to visualize and interact with the "
    "API and the underlying model."
) + LINKS


def get_fastapi_app(
    enable_doc: bool = True,
    enable_predict: bool = True,  # FIXME(aloga): check if these are honored
    base_path: str = "",
) -> fastapi.FastAPI:
    """Get the main app, based on FastAPI."""
    global APP

    if APP:
        return APP

    APP = fastapi.FastAPI(
        title="Model serving API endpoint",
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
        response_model=responses.VersionsAndLinks,
    )

    # Add a redirect from the old swagger.json to the new openapi.json
    APP.add_api_route(
        f"{base_path}/swagger.json",
        APP.openapi,
        methods=["GET"],
        summary="Get OpenAPI schema",
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
