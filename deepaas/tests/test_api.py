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

import pytest

import deepaas
from deepaas import api
from deepaas.model.v2 import wrapper as v2_wrapper
from deepaas.tests import fake_responses
from deepaas.tests import fake_v2_model


class TestApiV2:
    @pytest.fixture
    @staticmethod
    def wrapped_model():
        return v2_wrapper.ModelWrapper("deepaas-test", fake_v2_model.TestModel(), None)

    @pytest.fixture
    @staticmethod
    async def client(application, aiohttp_client):
        c = await aiohttp_client(application)
        return c

    @pytest.fixture
    @staticmethod
    async def application(monkeypatch):
        w = v2_wrapper.ModelWrapper("deepaas-test", fake_v2_model.TestModel(), None)

        monkeypatch.setattr(api, "APP", None)
        monkeypatch.setattr(deepaas.model, "V2_MODELS", {"deepaas-test": w})
        monkeypatch.setattr(deepaas.model, "register_v2_models", lambda x: None)

        app = await api.get_app(enable_doc=False, base_path="/custom")

        return app

    async def test_not_found(self, client):
        ret = await client.get("/api")
        assert 404 == ret.status

    async def test_predict_data(self, client):
        f = io.BytesIO(b"foo")
        ret = await client.post(
            "/custom/v2/models/deepaas-test/predict/",
            data={"data": (f, "foo.txt"), "parameter": 1},
        )
        assert 200 == ret.status

        json = await ret.json()

        assert "data" in json
        del json["data"]

        assert fake_responses.deepaas_test_predict == json

    async def test_get_metadata(self, client):
        meta = fake_responses.models_meta

        ret = await client.get("/custom/v2/models/")
        assert ret.status in [200, 201]

        ret_meta = await ret.json()
        ret_meta["models"][0]["links"][0]["href"] = "/v2/models/deepaas-test"

        assert meta == ret_meta

        ret = await client.get("/custom/v2/models/deepaas-test/")
        assert ret.status in [200, 201]

        ret_meta = await ret.json()
        ret_meta["links"][0]["href"] = "/v2/models/deepaas-test"

        assert meta["models"][0] == ret_meta
