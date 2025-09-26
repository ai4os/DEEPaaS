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

from deepaas import auth
from deepaas.api.v2 import responses
from deepaas import model


router = fastapi.APIRouter(prefix="/models")


@router.get(
    "/",
    summary="Return loaded models and its information",
    description="Return list of DEEPaaS loaded models. In previous versions, DEEPaaS "
    "could load several models and serve them on the same endpoint.",
    tags=["models"],
    response_model=responses.ModelList,
)
async def index_models(
    request: fastapi.Request,
    _: str = auth.get_auth_dependency(),
):
    """Return loaded models and its information."""

    name = model.V2_MODEL_NAME
    model_obj = model.V2_MODEL
    m = {
        "id": name,
        "name": name,
        "links": [
            {
                "rel": "self",
                "href": str(request.url_for("get_model/" + name)),
            }
        ],
    }
    meta = model_obj.get_metadata()
    m.update(meta)
    return {"models": [m]}


def _get_handler_for_model(model_name, model_obj):
    """Auxiliary function to get the handler for a model.

    This function returns a handler for a model that can be used to
    register the routes in the router.
    """

    class Handler(object):
        """Class to handle the model metadata endpoints."""

        model_name = None
        model_obj = None

        def __init__(self, model_name, model_obj):
            self.model_name = model_name
            self.model_obj = model_obj

        async def get(self, request: fastapi.Request, _: str = auth.get_auth_dependency()):
            """Return model's metadata."""
            m = {
                "id": self.model_name,
                "name": self.model_name,
                "links": [
                    {
                        "rel": "self",
                        "href": str(request.url),
                    }
                ],
            }
            meta = self.model_obj.get_metadata()
            m.update(meta)

            return m

        def register_routes(self, router):
            """Register routes for the model in the router."""
            router.add_api_route(
                f"/{self.model_name}",
                self.get,
                name="get_model/" + self.model_name,
                summary="Return model's metadata",
                tags=["models"],
                response_model=responses.ModelMeta,
            )

    return Handler(model_name, model_obj)


def get_router() -> fastapi.APIRouter:
    """Auxiliary function to get the router.

    We use this function to be able to include the router in the main
    application and do things before it gets included.

    In this case we explicitly include the model's endpoints.

    """
    model_name = model.V2_MODEL_NAME
    model_obj = model.V2_MODEL

    hdlr = _get_handler_for_model(model_name, model_obj)
    hdlr.register_routes(router)

    return router
