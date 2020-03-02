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

import uuid

from aiohttp import test_utils
from aiohttp import web
import deepaas
from deepaas.api import v1
import deepaas.model
from deepaas.tests import base


class TestApiV1(base.TestCase):
    async def get_application(self):
        deepaas.model.v1.register_models()

        app = web.Application(debug=True)
        v1app = v1.get_app()
        app.add_subapp("/v1", v1app)

        return app

    def assert_ok(self, response):
        self.assertIn(response.status, [200, 201])

    @test_utils.unittest_run_loop
    async def test_not_found(self):
        ret = await self.client.get("/v1/models/%s" % uuid.uuid4().hex)
        self.assertEqual(404, ret.status)

        ret = await self.client.put("/v1/models/%s" % uuid.uuid4().hex)
        self.assertEqual(404, ret.status)

        ret = await self.client.post("/v1/models/%s" % uuid.uuid4().hex)
        self.assertEqual(404, ret.status)

        ret = await self.client.delete("/v1/models/%s" % uuid.uuid4().hex)
        self.assertEqual(404, ret.status)

    @test_utils.unittest_run_loop
    async def test_model_not_found(self):
        ret = await self.client.put("/v1/models/%s/train" % uuid.uuid4().hex)
        self.assertEqual(404, ret.status)

        ret = await self.client.post("/v1/models/%s/predict" %
                                     uuid.uuid4().hex)
        self.assertEqual(404, ret.status)

        ret = await self.client.get("/v1/models/%s" % uuid.uuid4().hex)
        self.assertEqual(404, ret.status)

    @test_utils.unittest_run_loop
    async def test_train(self):
        ret = await self.client.put("/v1/models/deepaas-test/train")
        self.assertEqual(501, ret.status)

    @test_utils.unittest_run_loop
    async def test_predict_not_data(self):
        ret = await self.client.post("/v1/models/deepaas-test/predict")
        self.assertEqual(400, ret.status)

    @test_utils.unittest_run_loop
    async def test_predict_urls_not_implemented(self):
        ret = await self.client.post(
            "/v1/models/deepaas-test/predict",
            data={"url": "http://example.org/"})
        self.assertEqual(501, ret.status)

    @test_utils.unittest_run_loop
    async def test_predict_various_urls_not_implemented(self):
        ret = await self.client.post(
            "/v1/models/deepaas-test/predict",
            data={"url": ["http://example.org/", "http://example.com"]})
        self.assertEqual(501, ret.status)

    @test_utils.unittest_run_loop
    async def test_get_metadata(self):
        meta = {'models': [
            {'author': 'Alvaro Lopez Garcia',
             'description': ('This is not a model at all, just a '
                             'placeholder for testing the API '
                             'functionality. If you are seeing this, it is '
                             'because DEEPaaS could not load a valid model.'),
             'id': '0',
             'links': [{'href': '/v1/models/deepaas-test', 'rel': 'self'}],
             'name': 'deepaas-test',
             'version': '0.0.1'}
        ]}

        ret = await self.client.get("/v1/models")
        self.assert_ok(ret)
        self.assertDictEqual(meta, await ret.json())

        ret = await self.client.get("/v1/models/deepaas-test")
        self.assert_ok(ret)
        self.assertDictEqual(meta["models"][0], await ret.json())

    @test_utils.unittest_run_loop
    async def test_bad_metods_metadata(self):
        for i in (self.client.post, self.client.put, self.client.delete):
            ret = await i("/v1/models")
            self.assertEqual(405, ret.status)
