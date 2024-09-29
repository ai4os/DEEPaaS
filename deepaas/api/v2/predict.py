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
import fastapi.encoders
import fastapi.exceptions

from deepaas.api.v2 import responses
from deepaas.api.v2 import utils
from deepaas import model


def _get_model_response(model_name, model_obj):
    response_schema = model_obj.response_schema

    if response_schema is not None:
        return response_schema

    return responses.Prediction


router = fastapi.APIRouter(prefix="/models")


def _get_handler_for_model(model_name, model_obj):
    """Auxiliary function to get the handler for a model.

    This function returns a handler for a model that can be used to
    register the routes in the router.

    """

    user_declared_args = model_obj.get_predict_args()
    pydantic_schema = utils.get_pydantic_schema_from_marshmallow_fields(
        "PydanticSchema",
        user_declared_args,
    )

    class Handler(object):
        """Class to handle the model metadata endpoints."""

        model_name = None
        model_obj = None

        def __init__(self, model_name, model_obj):
            self.model_name = model_name
            self.model_obj = model_obj

        async def predict(self, args: pydantic_schema = fastapi.Depends()):
            """Make a prediction given the input data."""
            dict_args = args.model_dump(by_alias=True)

            ret = await self.model_obj.predict(**args.model_dump(by_alias=True))

            if isinstance(ret, model.v2.wrapper.ReturnedFile):
                ret = open(ret.filename, "rb")

            if self.model_obj.has_schema:
                # FIXME(aloga): Validation does not work, as we are converting from
                # Marshmallow to Pydantic, check this as son as possible.
                # self.model_obj.validate_response(ret)
                return fastapi.responses.JSONResponse(ret)

            return fastapi.responses.JSONResponse(
                content={"status": "OK", "predictions": ret}
            )

        def register_routes(self, router):
            """Register the routes in the router."""

            response = _get_model_response(self.model_name, self.model_obj)

            router.add_api_route(
                f"/{self.model_name}/predict",
                self.predict,
                methods=["POST"],
                response_model=response,
                tags=["models", "predict"]
            )

    return Handler(model_name, model_obj)


def get_router():
    """Auxiliary function to get the router.

    We use this function to be able to include the router in the main
    application and do things before it gets included.

    In this case we explicitly include the model precit endpoint.

    """
    model_name = model.V2_MODEL_NAME
    model_obj = model.V2_MODEL

    hdlr = _get_handler_for_model(model_name, model_obj)
    hdlr.register_routes(router)

    return router
