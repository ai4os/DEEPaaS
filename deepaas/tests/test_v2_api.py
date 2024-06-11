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
import pytest

import deepaas
from deepaas.api import v2
from deepaas.api.v2 import predict
from deepaas.api.v2 import responses
import deepaas.model
import deepaas.model.v2
from deepaas.model.v2 import wrapper as v2_wrapper
from deepaas.tests import fake_responses
from deepaas.tests import fake_v2_model

CONF = cfg.CONF
logging.register_options(CONF)


def test_loading_ok_with_missing_schema():
    class Fake(object):
        response_schema = None

    response = predict._get_model_response("deepaas-test", Fake)
    assert response is responses.Prediction


@pytest.fixture(autouse=True)
def cfg_fixture():
    def set_flag(flag, value):
        CONF.set_override(flag, value)

    return set_flag


class BaseTestApiV2:
    @pytest.fixture
    @staticmethod
    def wrapped_model():
        return v2_wrapper.ModelWrapper("deepaas-test", fake_v2_model.TestModel(), None)

    @pytest.fixture
    @staticmethod
    async def client(application, aiohttp_client):
        c = await aiohttp_client(application)
        return c

    async def test_get_metadata(self, client):
        meta = fake_responses.models_meta

        ret = await client.get("/v2/models/")
        assert ret.status in [200, 201]
        assert meta == await ret.json()

        ret = await client.get("/v2/models/deepaas-test/")
        assert ret.status in [200, 201]
        assert meta["models"][0] == await ret.json()

    async def test_predict_data(self, client):
        f = io.BytesIO(b"foo")
        ret = await client.post(
            "/v2/models/deepaas-test/predict/",
            data={"data": (f, "foo.txt"), "parameter": 1},
        )
        assert 200 == ret.status

        json = await ret.json()

        assert "data" in json
        del json["data"]

        assert fake_responses.deepaas_test_predict == json

    async def test_train(self, client):
        ret = await client.post("/v2/models/deepaas-test/train/", data={"sleep": 0})
        assert 200 == ret.status

        json = await ret.json()

        assert "date" in json
        json.pop("date")

        assert "uuid" in json
        json.pop("uuid")

        assert fake_responses.deepaas_test_train == json


class TestApiV2NoTrain(BaseTestApiV2):
    @pytest.fixture
    @staticmethod
    async def application(monkeypatch):
        app = web.Application()
        app.middlewares.append(web.normalize_path_middleware())

        w = v2_wrapper.ModelWrapper("deepaas-test", fake_v2_model.TestModel(), app)

        monkeypatch.setattr(deepaas.model, "V2_MODELS", {"deepaas-test": w})

        v2app = v2.get_app(enable_train=False)
        app.add_subapp("/v2", v2app)

        return app

    async def test_train(self, client):
        ret = await client.post("/v2/models/deepaas-test/train")
        assert 402 == ret.status


class TestApiV2NoPredict(BaseTestApiV2):
    @pytest.fixture
    @staticmethod
    async def application(monkeypatch):
        app = web.Application()
        app.middlewares.append(web.normalize_path_middleware())

        w = v2_wrapper.ModelWrapper("deepaas-test", fake_v2_model.TestModel(), app)

        monkeypatch.setattr(deepaas.model, "V2_MODELS", {"deepaas-test": w})

        v2app = v2.get_app(enable_predict=False)
        app.add_subapp("/v2", v2app)

        return app

    async def test_predict_data(self, client):
        ret = await client.post("/v2/models/deepaas-test/predict/")
        assert 402 == ret.status


class TestApiV2(BaseTestApiV2):
    @pytest.fixture
    @staticmethod
    async def application(monkeypatch):
        app = web.Application()
        app.middlewares.append(web.normalize_path_middleware())

        w = v2_wrapper.ModelWrapper("deepaas-test", fake_v2_model.TestModel(), app)

        monkeypatch.setattr(deepaas.model, "V2_MODELS", {"deepaas-test": w})

        v2app = v2.get_app()
        app.add_subapp("/v2", v2app)

        return app

    async def test_not_found(self, client):
        ret = await client.get("/v2/models/%s" % uuid.uuid4().hex)
        assert 404 == ret.status

        ret = await client.put("/v2/models/%s" % uuid.uuid4().hex)
        assert 404 == ret.status

        ret = await client.post("/v2/models/%s" % uuid.uuid4().hex)
        assert 404 == ret.status

        ret = await client.delete("/v2/models/%s" % uuid.uuid4().hex)
        assert 404 == ret.status

    async def test_model_not_found(self, client):
        ret = await client.get("/v2/models/%s/train" % uuid.uuid4().hex)
        assert 404 == ret.status

        ret = await client.put("/v2/models/%s/train" % uuid.uuid4().hex)
        assert 404 == ret.status

        ret = await client.post("/v2/models/%s/predict" % uuid.uuid4().hex)
        assert 404 == ret.status

        ret = await client.get("/v2/models/%s" % uuid.uuid4().hex)
        assert 404 == ret.status

    async def test_predict_no_parameters(self, client):
        ret = await client.post("/v2/models/deepaas-test/predict/")
        json = await ret.json()

        expected = {
            "parameter": ["Missing data for required field."],
            "data": ["Missing data for required field."],
        }
        assert 422 == ret.status
        assert expected == json

    async def test_bad_metods_metadata(self, client):
        for i in (client.post, client.put, client.delete):
            ret = await i("/v2/models/")
            assert 405 == ret.status
