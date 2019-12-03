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

from aiohttp import test_utils
from aiohttp import web
import marshmallow
from marshmallow import fields as m_fields
import mock
from webargs import fields

import deepaas
import deepaas.model.v2
from deepaas.model.v2 import base as v2_base
from deepaas.model.v2 import test as v2_test
from deepaas.model.v2 import wrapper as v2_wrapper
from deepaas.tests import base


class TestV2Model(base.TestCase):
    def setUp(self):
        super(TestV2Model, self).setUp()

        deepaas.model.v2.MODELS_LOADED = False
        deepaas.model.v2.MODELS = {}

    def test_abc(self):
        self.assertRaises(TypeError, v2_base.BaseModel)

    def test_not_implemented(self):
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
        self.assertRaises(NotImplementedError, m.get_metadata)
        self.assertRaises(NotImplementedError, m.predict)
        self.assertRaises(NotImplementedError, m.get_predict_args)
        self.assertRaises(NotImplementedError, m.train)
        self.assertRaises(NotImplementedError, m.get_train_args)

    def test_bad_schema(self):
        class Model(object):
            schema = []

        self.assertRaises(
            web.HTTPInternalServerError,
            v2_wrapper.ModelWrapper,
            "test", Model(),
            self.app
        )

    def test_validate_no_schema(self):
        class Model(object):
            schema = None

        wrapper = v2_wrapper.ModelWrapper("test", Model(), self.app)
        self.assertRaises(
            web.HTTPInternalServerError,
            wrapper.validate_response,
            None
        )

    def test_invalid_schema(self):
        class Model(object):
            schema = object()

        self.assertRaises(
            web.HTTPInternalServerError,
            v2_wrapper.ModelWrapper,
            "test", Model(),
            self.app
        )

    def test_marshmallow_schema(self):
        class Schema(marshmallow.Schema):
            foo = m_fields.Str()

        class Model(object):
            schema = Schema

        wrapper = v2_wrapper.ModelWrapper("test", Model(), self.app)

        self.assertTrue(wrapper.validate_response({"foo": "bar"}))
        self.assertRaises(
            web.HTTPInternalServerError,
            wrapper.validate_response,
            {"foo": 1.0}
        )

    def test_dict_schema(self):
        class Model(object):
            schema = {
                "foo": m_fields.Str()
            }

        wrapper = v2_wrapper.ModelWrapper("test", Model(), self.app)

        self.assertTrue(wrapper.validate_response({"foo": "bar"}))
        self.assertRaises(
            web.HTTPInternalServerError,
            wrapper.validate_response,
            {"foo": 1.0}
        )

    def test_dummy_model(self):
        m = v2_test.TestModel()
        self.assertDictEqual(
            {'date': '2019-01-1',
             'labels': [{'label': 'foo', 'probability': 1.0}]},
            m.predict()
        )
        self.assertIsNone(m.train())
        meta = m.get_metadata()
        self.assertIn("description", meta)
        self.assertIn("id", meta)
        self.assertIn("name", meta)
        self.assertEqual("Alvaro Lopez Garcia", meta["author"])
        pargs = m.get_predict_args()
        targs = m.get_train_args()
        for arg, val in itertools.chain(pargs.items(), targs.items()):
            self.assertIsInstance(val, fields.Field)

    @test_utils.unittest_run_loop
    async def test_dummy_model_with_wrapper(self):
        w = v2_wrapper.ModelWrapper("foo", v2_test.TestModel(), self.app)
        task = w.predict()
        await task
        ret = task.result()
        self.assertDictEqual(
            {'date': '2019-01-1',
             'labels': [{'label': 'foo', 'probability': 1.0}]},
            ret
        )
        task = w.train(sleep=0)
        await task
        ret = task.result()
        self.assertIsNone(ret)
        meta = w.get_metadata()
        self.assertIn("description", meta)
        self.assertIn("id", meta)
        self.assertIn("name", meta)
        pargs = w.get_predict_args()
        targs = w.get_train_args()
        for arg, val in itertools.chain(pargs.items(), targs.items()):
            self.assertIsInstance(val, fields.Field)

    @test_utils.unittest_run_loop
    async def test_model_with_not_implemented_attributes_and_wrapper(self):
        w = v2_wrapper.ModelWrapper("foo", object(), self.app)

        # NOTE(aloga): Cannot use assertRaises here directly, as testtools
        # overrides this method, and their implementation makes impossible to
        # use it a s context manager. Then, since we need to do async calls to
        # the methods (they are coroutines) we cannot use assertRaises
        # directly.
        try:
            await w.predict()
        except Exception as e:
            self.assertIsInstance(e, web.HTTPNotImplemented)

        try:
            await w.train()
        except Exception as e:
            self.assertIsInstance(e, web.HTTPNotImplemented)

        meta = w.get_metadata()
        self.assertIn("description", meta)
        self.assertIn("id", meta)
        self.assertIn("name", meta)
        pargs = w.get_predict_args()
        targs = w.get_train_args()
        for arg, val in itertools.chain(pargs.items(), targs.items()):
            self.assertIsInstance(val, fields.Field)

    @mock.patch('deepaas.model.loading.get_available_models')
    def test_loading_ok(self, mock_loading):
        mock_loading.return_value = {uuid.uuid4().hex: "bar"}
        deepaas.model.v2.register_models(self.app)
        mock_loading.assert_called()
        for m in deepaas.model.v2.MODELS.values():
            self.assertIsInstance(m, v2_wrapper.ModelWrapper)

    @mock.patch('deepaas.model.loading.get_available_models')
    def test_loading_ok_singleton(self, mock_loading):
        mock_loading.return_value = {uuid.uuid4().hex: "bar"}
        deepaas.model.v2.register_models(self.app)
        deepaas.model.v2.register_models(self.app)
        mock_loading.assert_called_once()
        for m in deepaas.model.v2.MODELS.values():
            self.assertIsInstance(m, v2_wrapper.ModelWrapper)

    @mock.patch('deepaas.model.loading.get_available_models')
    def test_loading_error(self, mock_loading):
        mock_loading.return_value = {}
        deepaas.model.v2.register_models(self.app)
        mock_loading.assert_called()
        self.assertIn("deepaas-test", deepaas.model.v2.MODELS)
        m = deepaas.model.v2.MODELS.pop("deepaas-test")
        self.assertIsInstance(m, v2_wrapper.ModelWrapper)
        self.assertIsInstance(m.model_obj, v2_test.TestModel)
