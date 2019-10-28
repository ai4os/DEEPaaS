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
from oslo_log import log

from deepaas.api.v2 import debug as v2_debug
from deepaas.api.v2 import models as v2_model
from deepaas.api.v2 import predict as v2_predict
from deepaas.api.v2 import responses
from deepaas.api.v2 import train as v2_train
from deepaas import model

CONF = cfg.CONF
LOG = log.getLogger("deepaas.api.v2")

# Get the models (this is a singleton, so it is safe to call it multiple times
model.register_v2_models()

APP = None


def get_app():
    global APP

    APP = web.Application()

#    # Add a text/plain representation so that we can return text as
#    # responses
#    @api.representation('text/plain')
#    def text_response(data, code, headers=None):
#        resp = flask.make_response(data, code)
#        resp.headers['Content-Type'] = 'text/plain'
#        return resp

    v2_debug.setup_debug()

    APP.router.add_get('/', get_version, name="v2")
    APP.add_routes(v2_debug.routes)
    APP.add_routes(v2_model.routes)
    APP.add_routes(v2_train.routes)
    APP.add_routes(v2_predict.routes)

    return APP


@aiohttp_apispec.docs(
    tags=["versions"],
    summary="Get V2 API version information",
)
@aiohttp_apispec.response_schema(responses.Version(), 200)
@aiohttp_apispec.response_schema(responses.Failure(), 400)
async def get_version(request):
    version = {
        "version": "stable",
        "id": "v2",
        "links": [
            {
                "rel": "self",
                # NOTE(aloga): we use our the router table from this
                # application (i.e. the global APP in this module) to be able
                # to build the correct url, as it can be prefixed outside of
                # this module (in an add_subapp() call)
                "href": "%s" % APP.router["v2"].url_for(),
            },
        ]
    }

# NOTE(aloga): skip these for now, until this issue is solved:
# https://github.com/maximdanilchenko/aiohttp-apispec/issues/65
#                doc = "%s.doc" % v.split(".")[0]
#            d = {"rel": "help",
#                 "type": "text/html",
#                 # FIXME(aloga): this -v is wrong
#                 "href": "flask.url_for(doc)"}
#            versions[-1]["links"].append(d)
#
#                specs = "%s.specs" % v.split(".")[0]
#            d = {"rel": "describedby",
#                 "type": "application/json",
#                 # FIXME(aloga): this -v is wrong
#                 "href": "flask.url_for(specs)"}
#            versions[-1]["links"].append(d)

    return web.json_response(version)
