# -*- coding: utf-8 -*-

# Copyright 2019 Spanish National Research Council (CSIC)
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

from aiohttp import web
import aiohttp_apispec

from deepaas.api.v2 import responses

app = web.Application()
routes = web.RouteTableDef()


@routes.view('/')
class Versions(web.View):

    versions = {}

    def __init__(self, *args, wsk_args=None, **kwargs):
        super(Versions, self).__init__(*args, **kwargs)

    @aiohttp_apispec.docs(
        tags=["versions"],
        summary="Get available API versions",
    )
    @aiohttp_apispec.response_schema(responses.Versions(), 200)
    @aiohttp_apispec.response_schema(responses.Failure(), 400)
    async def get(self):
        versions = []
        for ver, info in self.versions.items():
            resp = await info(self.request)
            versions.append(json.loads(resp.body))

        response = {
            "versions": versions,
            "links": []
        }
        # But here we use the global app coming in the request
        doc = self.request.app.router.named_resources().get("swagger.docs")
        if doc:
            doc = {
                "rel": "help",
                "type": "text/html",
                "href": "%s" % doc.url_for()
            }
            response["links"].append(doc)

        spec = self.request.app.router.named_resources().get("swagger.spec")
        if spec:
            spec = {
                "rel": "describedby",
                "type": "application/json",
                "href": "%s" % spec.url_for(),
            }
            response["links"].append(spec)

        return web.json_response(response)


def register_version(version, func):
    # NOTE(aloga): we could use a @classmethod on Versions, but it fails
    # with a TypeError: 'classmethod' object is not callable since the function
    # is decorated.
    Versions.versions[version] = func
