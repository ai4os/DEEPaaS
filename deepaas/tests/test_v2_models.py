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

import itertools
import uuid

from aiohttp import web
import marshmallow
from marshmallow import fields as m_fields
import pytest
from webargs import fields

import deepaas
from deepaas import exceptions
import deepaas.model.v2
from deepaas.model.v2 import base as v2_base
from deepaas.model.v2 import wrapper as v2_wrapper
from deepaas.tests import fake_v2_model


@pytest.fixture
async def application():
    app = web.Application()
    app.middlewares.append(web.normalize_path_middleware())

    return app


@pytest.fixture
async def mocks(monkeypatch):
    monkeypatch.setattr(v2_wrapper.ModelWrapper, "_setup_cleanup", lambda x: None)
    model_name = uuid.uuid4().hex
    monkeypatch.setattr(
        deepaas.model.loading,
        "get_available_models",
        lambda x: {model_name: "foo"},
    )
    monkeypatch.setattr(
        deepaas.model.loading,
        "get_available_model_names",
        lambda x: [model_name],
    )
    monkeypatch.setattr(
        deepaas.model.loading,
        "get_model_by_name",
        lambda x, y: fake_v2_model.TestModel,
    )
    monkeypatch.setattr(deepaas.model.v2, "MODELS_LOADED", False)
    monkeypatch.setattr(deepaas.model.v2, "MODELS", {})


def test_abc():
    with pytest.raises(TypeError):
        v2_base.BaseModel()


def test_not_implemented():
    class Model(v2_base.BaseModel):
        def get_metadata(self):
            super(Model, self).get_metadata()

        def predict(self, **kwargs):
            super(Model, self).predict(**kwargs)

        def get_predict_args(self):
            super(Model, self).get_predict_args()

        def train(self, **kwargs):
            super(Model, self).train(**kwargs)

        def warm(self, **kwargs):
            super(Model, self).train(**kwargs)

        def get_train_args(self):
            super(Model, self).get_train_args()

    m = Model()

    with pytest.raises(NotImplementedError):
        m.get_metadata()
    with pytest.raises(NotImplementedError):
        m.predict()
    with pytest.raises(NotImplementedError):
        m.get_predict_args()
    with pytest.raises(NotImplementedError):
        m.train()
    with pytest.raises(NotImplementedError):
        m.get_train_args()


async def test_bad_schema(application, mocks):
    class Model(object):
        schema = []

    with pytest.raises(web.HTTPInternalServerError):
        v2_wrapper.ModelWrapper("test", Model(), application)


async def test_validate_no_schema(application, mocks):
    class Model(object):
        schema = None

    with pytest.raises(web.HTTPInternalServerError):
        wrapper = v2_wrapper.ModelWrapper("test", Model(), application)
        wrapper.validate_response(None)


async def test_invalid_schema(application, mocks):
    class Model(object):
        schema = object()

    with pytest.raises(web.HTTPInternalServerError):
        v2_wrapper.ModelWrapper("test", Model(), application)


async def test_marshmallow_schema(application, mocks):
    class Schema(marshmallow.Schema):
        foo = m_fields.Str()

    class Model(object):
        schema = Schema

    wrapper = v2_wrapper.ModelWrapper("test", Model(), application)

    assert wrapper.validate_response({"foo": "bar"})
    with pytest.raises(web.HTTPInternalServerError):
        wrapper.validate_response({"foo": 1.0})


async def test_dict_schema(application, mocks):
    class Model(object):
        schema = {"foo": m_fields.Str()}

    wrapper = v2_wrapper.ModelWrapper("test", Model(), application)

    assert wrapper.validate_response({"foo": "bar"})
    with pytest.raises(web.HTTPInternalServerError):
        wrapper.validate_response({"foo": 1.0})


@pytest.fixture
def model():
    return fake_v2_model.TestModel()


async def test_dummy_model(model, mocks):
    pred = model.predict()
    pred.pop("data")
    assert pred == {
        "date": "2019-01-1",
        "labels": [{"label": "foo", "probability": 1.0}],
    }

    assert model.train() is None

    meta = model.get_metadata()
    assert "description" in meta
    assert "id" in meta
    assert "name" in meta
    assert "Alvaro Lopez Garcia" == meta["author"]

    pargs = model.get_predict_args()
    targs = model.get_train_args()
    for _arg, val in itertools.chain(pargs.items(), targs.items()):
        assert isinstance(val, fields.Field)


async def test_dummy_model_with_wrapper(application, model, mocks):
    w = v2_wrapper.ModelWrapper("foo", model, application)
    task = w.predict()
    await task
    ret = task.result()["output"]
    del ret["data"]
    assert ret == {
        "date": "2019-01-1",
        "labels": [{"label": "foo", "probability": 1.0}],
    }
    task = w.train(sleep=0)
    await task
    ret = task.result()
    assert ret["output"] is None
    meta = w.get_metadata()
    assert "description" in meta
    assert "id" in meta
    assert "name" in meta
    pargs = w.get_predict_args()
    targs = w.get_train_args()
    for _arg, val in itertools.chain(pargs.items(), targs.items()):
        print(val)
        print(fields.Field)
        assert isinstance(val, fields.Field)


async def test_model_with_not_implemented_attributes_and_wrapper(application, mocks):
    w = v2_wrapper.ModelWrapper("foo", object(), application)

    with pytest.raises(web.HTTPNotImplemented):
        await w.predict()
    with pytest.raises(web.HTTPNotImplemented):
        await w.train()

    meta = w.get_metadata()
    assert "description" in meta
    assert "id" in meta
    assert "name" in meta
    pargs = w.get_predict_args()
    targs = w.get_train_args()
    for _arg, val in itertools.chain(pargs.items(), targs.items()):
        assert isinstance(val, fields.Field)


async def test_loading_ok(application, mocks):
    deepaas.model.v2.register_models(application)

    for m in deepaas.model.v2.MODELS.values():
        assert isinstance(m, v2_wrapper.ModelWrapper)


async def test_loading_ok_singleton(application, mocks, monkeypatch):
    deepaas.model.v2.register_models(application)
    new_model_name = uuid.uuid4().hex
    monkeypatch.setattr(
        deepaas.model.loading,
        "get_available_models",
        lambda x: {new_model_name: "barz"},
    )
    deepaas.model.v2.register_models(application)

    for name, m in deepaas.model.v2.MODELS.items():
        assert isinstance(m, v2_wrapper.ModelWrapper)
        assert name != new_model_name


def test_loading_error(application, monkeypatch):
    monkeypatch.setattr(deepaas.model.loading, "get_available_models", lambda x: {})
    with pytest.raises(exceptions.NoModelsAvailable):
        deepaas.model.v2.register_models(application)
