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


from aiohttp import test_utils
from aiohttp import web
import aiohttp_apispec

from deepaas.api import v1
from deepaas.api import v2
from deepaas.api import versions
from deepaas.tests import base
from deepaas.tests import fake_responses


class TestApiVersions(base.TestCase):
    async def get_application(self):
        app = web.Application(debug=True)
        app.add_routes(versions.routes)

        app.add_subapp("/v1", v1.get_app())
        app.add_subapp("/v2", v2.get_app())

        versions.Versions.versions = {}

        aiohttp_apispec.setup_aiohttp_apispec(
            app=app,
            url="/swagger.json",
            swagger_path="/ui"
        )

        return app

    @test_utils.unittest_run_loop
    async def test_get_no_versions(self):
        ret = await self.client.get("/")
        self.assertEqual(200, ret.status)
        self.assertDictEqual(fake_responses.empty_versions, await ret.json())

    @test_utils.unittest_run_loop
    async def test_v1_version(self):
        versions.register_version("deprecated", v1.get_version)
        ret = await self.client.get("/")
        self.assertEqual(200, ret.status)
        expect = {
            'versions': [
                fake_responses.v1_version
            ]
        }
        resp = await ret.json()
        resp.pop("links")
        self.assertDictEqual(expect, resp)

    @test_utils.unittest_run_loop
    async def test_v2_version(self):
        versions.register_version("stable", v2.get_version)
        ret = await self.client.get("/")
        self.assertEqual(200, ret.status)
        expect = fake_responses.versions
        self.assertDictEqual(expect, await ret.json())
