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

from deepaas import model


def setup_routes(app):
    # In the next lines we iterate over the loaded models and create the
    # different resources for each model. This way we can also load the
    # expected parameters if needed (as in the training method).
    for model_name, model_obj in model.V2_MODELS.items():
        args = webargs.core.dict2schema(model_obj.get_train_args())

        class Handler(object):
            model_name = None
            model_obj = None

            def __init__(self, model_name, model_obj):
                self.model_name = model_name
                self.model_obj = model_obj

            @aiohttp_apispec.docs(
                tags=["models"],
                summary="Retrain model with available data"
            )
            @aiohttp_apispec.querystring_schema(args)
            @aiohttpparser.parser.use_args(args)
            async def post(self, request, args):
                ret = await self.model_obj.train(**args)
                # FIXME(aloga): what are we returning here? We need to take
                # care of these responses as well.
                return web.json_response(ret)

        hdlr = Handler(model_name, model_obj)
        app.router.add_post("/models/%s/train" % model_name, hdlr.post)
