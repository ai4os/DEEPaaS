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

import flask_restplus.reqparse
import mock
import werkzeug.exceptions as exceptions

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

            def add_predict_args(self, parser):
                super(Model, self).add_predict_args(parser)

            def train(self, **kwargs):
                super(Model, self).train(**kwargs)

            def add_train_args(self, parser):
                super(Model, self).add_train_args(parser)

        m = Model()
        self.assertRaises(NotImplementedError, m.get_metadata)
        self.assertRaises(NotImplementedError, m.predict)
        self.assertIsNone(m.add_predict_args(None))
        self.assertRaises(NotImplementedError, m.train)
        self.assertIsNone(m.add_train_args(None))

    def test_bad_schema(self):
        class Model(object):
            response = []

        self.assertRaises(exceptions.InternalServerError,
                          v2_model.ModelWrapper,
                          "test", Model())

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
        parser = flask_restplus.reqparse.RequestParser()
        self.assertEqual(parser, m.add_train_args(parser))
        self.assertEqual(parser, m.add_predict_args(parser))

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
        parser = flask_restplus.reqparse.RequestParser()
        self.assertEqual(parser, w.add_train_args(parser))
        self.assertEqual(parser, w.add_predict_args(parser))

    def test_model_with_not_implemented_attributes_and_wrapper(self):
        w = v2_model.ModelWrapper("foo", object())
        self.assertRaises(exceptions.NotImplemented, w.predict)
        self.assertRaises(exceptions.NotImplemented, w.train)
        meta = w.get_metadata()
        self.assertIn("description", meta)
        self.assertIn("id", meta)
        self.assertIn("name", meta)
        fake_parser = object()
        self.assertEqual(fake_parser, w.add_train_args(fake_parser))
        self.assertEqual(fake_parser, w.add_predict_args(fake_parser))

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
