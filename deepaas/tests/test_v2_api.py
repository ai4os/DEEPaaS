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

import io
import uuid

from aiohttp import web
from oslo_config import cfg
from oslo_log import log as logging

import deepaas
from deepaas.api import v2
from deepaas.api.v2 import predict
from deepaas.api.v2 import responses
import deepaas.model
import deepaas.model.v2
from deepaas.tests import base
from deepaas.tests import fake_responses

CONF = cfg.CONF
logging.register_options(CONF)


def test_loading_ok_with_missing_schema():
    class Fake(object):
        response_schema = None

    response = predict._get_model_response("deepaas-test", Fake)
    assert response is responses.Prediction


class TestApiV2NoTrain(base.TestCase):
    async def get_application(self):
        app = web.Application(debug=True)
        app.middlewares.append(web.normalize_path_middleware())

        deepaas.model.v2.register_models(app)

        v2app = v2.get_app(enable_train=False)
        app.add_subapp("/v2", v2app)

        return app

    def setUp(self):
        super(TestApiV2NoTrain, self).setUp()

        self.maxDiff = None

        self.flags(debug=True)

    def assert_ok(self, response):
        self.assertIn(response.status, [200, 201])

    async def test_not_found(self):
        ret = await self.client.post("/v2/models/deepaas-test/train")
        self.assertEqual(404, ret.status)

    async def test_predict_data(self):
        f = io.BytesIO(b"foo")
        ret = await self.client.post(
            "/v2/models/deepaas-test/predict/",
            data={"data": (f, "foo.txt"), "parameter": 1},
        )
        json = await ret.json()
        self.assertEqual(200, ret.status)
        self.assertDictEqual(fake_responses.deepaas_test_predict, json)

    async def test_get_metadata(self):
        meta = fake_responses.models_meta

        ret = await self.client.get("/v2/models/")
        self.assert_ok(ret)
        self.assertDictEqual(meta, await ret.json())

        ret = await self.client.get("/v2/models/deepaas-test/")
        self.assert_ok(ret)
        self.assertDictEqual(meta["models"][0], await ret.json())


class TestApiV2NoPredict(base.TestCase):
    async def get_application(self):
        app = web.Application(debug=True)
        app.middlewares.append(web.normalize_path_middleware())

        deepaas.model.v2.register_models(app)

        v2app = v2.get_app(enable_predict=False)
        app.add_subapp("/v2", v2app)

        return app

    def setUp(self):
        super(TestApiV2NoPredict, self).setUp()

        self.maxDiff = None

        self.flags(debug=True)

    def assert_ok(self, response):
        self.assertIn(response.status, [200, 201])

    async def test_not_found(self):
        ret = await self.client.post("/v2/models/deepaas-test/predict/")
        self.assertEqual(404, ret.status)

    async def test_train(self):
        ret = await self.client.post(
            "/v2/models/deepaas-test/train/", data={"sleep": 0}
        )
        self.assertEqual(200, ret.status)
        json = await ret.json()
        json.pop("date")
        self.assertDictEqual(fake_responses.deepaas_test_train, json)

    async def test_get_metadata(self):
        meta = fake_responses.models_meta

        ret = await self.client.get("/v2/models/")
        self.assert_ok(ret)
        self.assertDictEqual(meta, await ret.json())

        ret = await self.client.get("/v2/models/deepaas-test/")
        self.assert_ok(ret)
        self.assertDictEqual(meta["models"][0], await ret.json())


class TestApiV2NoDoc(base.TestCase):
    async def get_application(self):
        app = web.Application(debug=True)
        app.middlewares.append(web.normalize_path_middleware())

        deepaas.model.v2.register_models(app)

        v2app = v2.get_app(enable_doc=False)
        app.add_subapp("/v2", v2app)

        return app

    def setUp(self):
        super(TestApiV2NoDoc, self).setUp()

        self.maxDiff = None

        self.flags(debug=True)

    def assert_ok(self, response):
        self.assertIn(response.status, [200, 201])

    async def test_not_found(self):
        ret = await self.client.get("/api")
        self.assertEqual(404, ret.status)


class TestApiV2CusomBasePath(base.TestCase):
    async def get_application(self):
        app = web.Application(debug=True)
        app.middlewares.append(web.normalize_path_middleware())

        deepaas.model.v2.register_models(app)

        v2app = v2.get_app(base_path="/custom")
        app.add_subapp("/v2", v2app)

        return app

    def setUp(self):
        super(TestApiV2CusomBasePath, self).setUp()

        self.maxDiff = None

        self.flags(debug=True)

    def assert_ok(self, response):
        self.assertIn(response.status, [200, 201])

    async def test_predict_data(self):
        f = io.BytesIO(b"foo")
        ret = await self.client.post(
            "/custom/v2/models/deepaas-test/predict/",
            data={"data": (f, "foo.txt"), "parameter": 1},
        )
        json = await ret.json()
        self.assertEqual(200, ret.status)
        self.assertDictEqual(fake_responses.deepaas_test_predict, json)

    async def test_train(self):
        ret = await self.client.post(
            "/custom/v2/models/deepaas-test/train/", data={"sleep": 0}
        )
        self.assertEqual(200, ret.status)
        json = await ret.json()
        json.pop("date")
        self.assertDictEqual(fake_responses.deepaas_test_train, json)

    async def test_get_metadata(self):
        meta = fake_responses.models_meta

        ret = await self.client.get("/custom/v2/models/")
        self.assert_ok(ret)
        self.assertDictEqual(meta, await ret.json())

        ret = await self.client.get("/custom/v2/models/deepaas-test/")
        self.assert_ok(ret)
        self.assertDictEqual(meta["models"][0], await ret.json())


class TestApiV2(base.TestCase):
    async def get_application(self):
        app = web.Application(debug=True)
        app.middlewares.append(web.normalize_path_middleware())

        deepaas.model.v2.register_models(app)

        v2app = v2.get_app()
        app.add_subapp("/v2", v2app)

        return app

    def setUp(self):
        super(TestApiV2, self).setUp()

        self.maxDiff = None

        self.flags(debug=True)

    def assert_ok(self, response):
        self.assertIn(response.status, [200, 201])

    async def test_not_found(self):
        ret = await self.client.get("/v2/models/%s" % uuid.uuid4().hex)
        self.assertEqual(404, ret.status)

        ret = await self.client.put("/v2/models/%s" % uuid.uuid4().hex)
        self.assertEqual(404, ret.status)

        ret = await self.client.post("/v2/models/%s" % uuid.uuid4().hex)
        self.assertEqual(404, ret.status)

        ret = await self.client.delete("/v2/models/%s" % uuid.uuid4().hex)
        self.assertEqual(404, ret.status)

    async def test_model_not_found(self):
        ret = await self.client.put("/v2/models/%s/train" % uuid.uuid4().hex)
        self.assertEqual(404, ret.status)

        ret = await self.client.post("/v2/models/%s/predict" % uuid.uuid4().hex)
        self.assertEqual(404, ret.status)

        ret = await self.client.get("/v2/models/%s" % uuid.uuid4().hex)
        self.assertEqual(404, ret.status)

    async def test_predict_no_parameters(self):
        ret = await self.client.post("/v2/models/deepaas-test/predict/")
        json = await ret.json()
        print(json)
        self.assertDictEqual(
            {
                "parameter": ["Missing data for required field."],
                "data": ["Missing data for required field."],
            },
            json,
        )
        self.assertEqual(422, ret.status)

    async def test_predict_data(self):
        f = io.BytesIO(b"foo")
        ret = await self.client.post(
            "/v2/models/deepaas-test/predict/",
            data={"data": (f, "foo.txt"), "parameter": 1},
        )
        json = await ret.json()
        self.assertEqual(200, ret.status)
        self.assertDictEqual(fake_responses.deepaas_test_predict, json)

    async def test_train(self):
        ret = await self.client.post(
            "/v2/models/deepaas-test/train/", data={"sleep": 0}
        )
        self.assertEqual(200, ret.status)
        json = await ret.json()
        json.pop("date")
        self.assertDictEqual(fake_responses.deepaas_test_train, json)

    async def test_get_metadata(self):
        meta = fake_responses.models_meta

        ret = await self.client.get("/v2/models/")
        self.assert_ok(ret)
        self.assertDictEqual(meta, await ret.json())

        ret = await self.client.get("/v2/models/deepaas-test/")
        self.assert_ok(ret)
        self.assertDictEqual(meta["models"][0], await ret.json())

    async def test_bad_metods_metadata(self):
        for i in (self.client.post, self.client.put, self.client.delete):
            ret = await i("/v2/models/")
            self.assertEqual(405, ret.status)
