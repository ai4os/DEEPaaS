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
import mock
from webargs import fields

import deepaas
from deepaas.model import v2 as v2_model
from deepaas.model.v2 import base as v2_base
from deepaas.model.v2 import test as v2_test
from deepaas.tests import base


class TestV2Model(base.TestCase):
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
            v2_model.ModelWrapper,
            "test", Model()
        )

    def test_validate_no_schema(self):
        class Model(object):
            schema = None

        wrapper = v2_model.ModelWrapper("test", Model())
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
            v2_model.ModelWrapper,
            "test", Model()
        )

    def test_marshmallow_schema(self):
        class Schema(marshmallow.Schema):
            foo = m_fields.Str()

        class Model(object):
            schema = Schema

        wrapper = v2_model.ModelWrapper("test", Model())

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

        wrapper = v2_model.ModelWrapper("test", Model())

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

    def test_dummy_model_with_wrapper(self):
        w = v2_model.ModelWrapper("foo", v2_test.TestModel())
        self.assertDictEqual(
            {'date': '2019-01-1',
             'labels': [{'label': 'foo', 'probability': 1.0}]},
            w.predict()
        )
        self.assertIsNone(w.train())
        meta = w.get_metadata()
        self.assertIn("description", meta)
        self.assertIn("id", meta)
        self.assertIn("name", meta)
        pargs = w.get_predict_args()
        targs = w.get_train_args()
        for arg, val in itertools.chain(pargs.items(), targs.items()):
            self.assertIsInstance(val, fields.Field)

    def test_model_with_not_implemented_attributes_and_wrapper(self):
        w = v2_model.ModelWrapper("foo", object())
        self.assertRaises(web.HTTPNotImplemented, w.predict)
        self.assertRaises(web.HTTPNotImplemented, w.train)
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
        deepaas.model.v2.register_models()
        for m in deepaas.model.v2.MODELS.values():
            self.assertIsInstance(m, v2_model.ModelWrapper)

    @mock.patch('deepaas.model.loading.get_available_models')
    def test_loading_error(self, mock_loading):
        mock_loading.return_value = []
        deepaas.model.v2.register_models()
        self.assertIn("deepaas-test", deepaas.model.v2.MODELS)
        m = deepaas.model.v2.MODELS.pop("deepaas-test")
        self.assertIsInstance(m, v2_model.ModelWrapper)
        self.assertIsInstance(m.model, v2_test.TestModel)
