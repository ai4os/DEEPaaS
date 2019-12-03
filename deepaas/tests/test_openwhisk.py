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

import copy
import json
import mock

from aiohttp import test_utils
from aiohttp import web

from deepaas.openwhisk import proxy
from deepaas.tests import base
from deepaas.tests import fake_responses


class AsyncMock(mock.MagicMock):
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)


class TestOpenWhiskProxy(base.TestCase):
    async def get_application(self):

        app = web.Application(debug=True)
        app.initialized = False
        app.add_routes(proxy.routes)

        return app

    def setUp(self):
        super(TestOpenWhiskProxy, self).setUp()

        self.maxDiff = None

        self.flags(debug=True)

        proxy.APP = None

    def get_wsk_args(self, path):
        return {
            "value": {
                "__ow_headers": {},
                "__ow_method": "get",
                "__ow_path": path,
            }
        }

    def assertJSON(self, expected, actual):
        jr = copy.deepcopy(actual)
        jr["body"] = json.loads(jr["body"])
        self.assertDictEqual(expected, jr)

    @test_utils.unittest_run_loop
    async def test_init(self):
        ret = await self.client.post("/init")
        self.assertEqual(200, ret.status)
        txt = await ret.text()
        self.assertEqual("OK", txt)

    def test_mock(self):
        with mock.patch(
            'deepaas.api.get_app',
            new_callable=AsyncMock
        ) as m_get_app:
            m_get_app.side_effect = Exception("K-Boom")

            async def test_init_failure():
                ret = await self.client.post("/init")
                self.assertEqual(500, ret.status)
                self.assertDictEqual(
                    {'error': 'Internal error. K-Boom'},
                    await ret.json()
                )

            self.loop.run_until_complete(test_init_failure())
            m_get_app.assert_called()

    def test_run_no_app(self):
        async def do_test():
            ret = await self.client.post("/run")
            self.assertEqual(502, ret.status)
        self.loop.run_until_complete(do_test())

    def test_run_no_data(self):
        async def do_test():
            ret = await self.client.post("/init")
            ret = await self.client.post("/run")
            self.assertEqual(400, ret.status)
        self.loop.run_until_complete(do_test())

    def test_run_versions(self):
        async def do_test():
            data = self.get_wsk_args("/")
            ret = await self.client.post("/init")
            ret = await self.client.post("/run", json=data)
            body = fake_responses.versions
            resp = {
                'body': body,
                'headers': {'Content-Type': 'application/json; charset=utf-8'},
                'statusCode': 200
            }
            self.assertJSON(resp, await ret.json())
        self.loop.run_until_complete(do_test())

    def test_run_version_v2(self):
        async def do_test():
            data = self.get_wsk_args("/v2/")
            ret = await self.client.post("/init")
            ret = await self.client.post("/run", json=data)
            body = fake_responses.v2_version
            resp = {
                'body': body,
                'headers': {'Content-Type': 'application/json; charset=utf-8'},
                'statusCode': 200
            }
            self.assertJSON(resp, await ret.json())
        self.loop.run_until_complete(do_test())

    def test_run_models(self):
        async def do_test():
            data = self.get_wsk_args("/v2/models")
            ret = await self.client.post("/init")
            ret = await self.client.post("/run", json=data)
            body = fake_responses.models_meta
            resp = {
                'body': body,
                'headers': {'Content-Type': 'application/json; charset=utf-8'},
                'statusCode': 200
            }
            self.assertJSON(resp, await ret.json())
        self.loop.run_until_complete(do_test())

    def test_run_models_deepaas(self):
        async def do_test():
            data = self.get_wsk_args("/v2/models/deepaas-test")
            ret = await self.client.post("/init")
            ret = await self.client.post("/run", json=data)
            body = fake_responses.deepaas_test_meta
            resp = {
                'body': body,
                'headers': {'Content-Type': 'application/json; charset=utf-8'},
                'statusCode': 200
            }
            self.assertJSON(resp, await ret.json())
        self.loop.run_until_complete(do_test())

    # TODO(aloga): test train and predict
