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

import fastapi
import fastapi.responses
from oslo_config import cfg

from deepaas.api.v2 import debug as v2_debug
from deepaas.api.v2 import models as v2_model
from deepaas.api.v2 import predict as v2_predict
from deepaas.api.v2 import responses

from deepaas import log

CONF = cfg.CONF
LOG = log.getLogger("deepaas.api.v2")

# NOTE(aloga): singleton pattern for the FastAPI app
APP = None


def get_app():
    global APP

    APP = fastapi.APIRouter()

    v2_debug.setup_debug()

    APP.include_router(v2_debug.get_router(), tags=["debug"])
    APP.include_router(v2_model.get_router(), tags=["models"])
    APP.include_router(v2_predict.get_router(), tags=["predict"])

    APP.add_api_route(
        "/",
        get_v2_version,
        methods=["GET"],
        tags=["version"],
        response_model=responses.Versions,
    )

    return APP


def get_v2_version(request: fastapi.Request) -> fastapi.responses.JSONResponse:
    root = str(request.url_for("get_v2_version"))
    version = {
        "version": "stable",
        "id": "v2",
        "links": [
            {
                "rel": "self",
                "type": "application/json",
                "href": f"{root}",
            }
        ],
    }
    return fastapi.responses.JSONResponse(content=version)
