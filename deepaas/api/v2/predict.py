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
from webargs import aiohttpparser
import webargs.core

from deepaas.api.v2 import responses
from deepaas import model


def _get_model_response(model_name, model_obj):
    response_schema = model_obj.response_schema

    if response_schema is not None:
        return response_schema

    return responses.Prediction


def _get_handler(model_name, model_obj):
    args = webargs.core.dict2schema(model_obj.get_predict_args())
    response = _get_model_response(model_name, model_obj)

    class Handler(object):
        model_name = None
        model_obj = None

        def __init__(self, model_name, model_obj):
            self.model_name = model_name
            self.model_obj = model_obj

        @aiohttp_apispec.docs(
            tags=["models"],
            summary="Make a prediction given the input data"
        )
        @aiohttp_apispec.querystring_schema(args)
        @aiohttp_apispec.response_schema(response(), 200)
        @aiohttp_apispec.response_schema(responses.Failure(), 400)
        @aiohttpparser.parser.use_args(args)
        async def post(self, request, args):
            task = self.model_obj.predict(**args)
            await task

            ret = task.result()

            if self.model_obj.has_schema:
                self.model_obj.validate_response(ret)
                return web.json_response(ret)

            return web.json_response({"status": "OK", "predictions": ret})

    return Handler(model_name, model_obj)


def setup_routes(app):
    # In the next lines we iterate over the loaded models and create the
    # different resources for each model. This way we can also load the
    # expected parameters if needed (as in the training method).
    for model_name, model_obj in model.V2_MODELS.items():
        hdlr = _get_handler(model_name, model_obj)
        app.router.add_post("/models/%s/predict" % model_name, hdlr.post)
