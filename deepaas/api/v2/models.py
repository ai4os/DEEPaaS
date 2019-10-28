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

from deepaas.api.v2 import responses
from deepaas import model

# Get the models (this is a singleton, so it is safe to call it multiple times
model.register_v2_models()

app = web.Application()
routes = web.RouteTableDef()


@aiohttp_apispec.docs(
    tags=["models"],
    summary="Return loaded models and its information",
    description="DEEPaaS can load several models and server them on the same "
                "endpoint, making a call to the root of the models namespace "
                "will return the loaded models, as long as their basic "
                "metadata.",
)
@routes.get('/models')
@aiohttp_apispec.response_schema(responses.ModelMeta(), 200)
async def get(request):
    """Return loaded models and its information.

    DEEPaaS can load several models and server them on the same endpoint,
    making a call to the root of the models namespace will return the
    loaded models, as long as their basic metadata.
    """

    models = []
    for name, obj in model.V2_MODELS.items():
        m = {
            "id": name,
            "name": name,
            "links": [{
                "rel": "self",
                "href": "%s/%s" % (request.path, name),
            }]
        }
        meta = obj.get_metadata()
        m.update(meta)
        models.append(m)
    return web.json_response({"models": models})


# In the next lines we iterate over the loaded models and create the different
# resources for each model. This way we can also load the expected parameters
# if needed (as in the training method).
for model_name, model_obj in model.V2_MODELS.items():
    @routes.view('/models/%s' % model_name)
    class BaseModel(web.View):
        model_name = model_name
        model_obj = model_obj

        @aiohttp_apispec.docs(
            tags=["models"],
            summary="Return '%s' model metadata" % model_name,
        )
        @aiohttp_apispec.response_schema(responses.ModelMeta(), 200)
        async def get(self):
            m = {
                "id": self.model_name,
                "name": self.model_name,
                "links": [{
                    "rel": "self",
                    "href": "%s" % self.request.path,
                }]
            }
            meta = self.model_obj.get_metadata()
            m.update(meta)

            return web.json_response(m)
