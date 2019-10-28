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

from aiohttp import web
import mock

import deepaas
import deepaas.model.v1
from deepaas.tests import base


class TestModel(base.TestCase):
    def test_abc(self):
        self.assertRaises(TypeError, deepaas.model.v1.BaseModel)

    def test_dummy_model(self):
        m = deepaas.model.v1.TestModel()
        for meth in (m.predict_file, m.predict_url, m.predict_data):
            self.assertRaises(NotImplementedError, meth, None)
        self.assertRaises(NotImplementedError, m.train)
        meta = m.get_metadata()
        self.assertIn("description", meta)
        self.assertIn("id", meta)
        self.assertIn("name", meta)
        self.assertEqual("Alvaro Lopez Garcia", meta["author"])
        self.assertEqual({}, m.get_train_args())
        self.assertEqual({}, m.get_test_args())

    def test_dummy_model_with_wrapper(self):
        w = deepaas.model.v1.ModelWrapper("foo", deepaas.model.v1.TestModel())
        for meth in (w.predict_file, w.predict_url, w.predict_data):
            self.assertRaises(web.HTTPNotImplemented, meth, None)
        self.assertRaises(web.HTTPNotImplemented, w.train)
        meta = w.get_metadata()
        self.assertIn("description", meta)
        self.assertIn("id", meta)
        self.assertIn("name", meta)
        self.assertEqual({}, w.get_train_args())
        self.assertEqual({}, w.get_test_args())

    def test_model_with_not_implemented_attributes_and_wrapper(self):
        w = deepaas.model.v1.ModelWrapper("foo", object())
        for meth in (w.predict_file, w.predict_url, w.predict_data):
            self.assertRaises(web.HTTPNotImplemented, meth, None)
        self.assertRaises(web.HTTPNotImplemented, w.train)
        meta = w.get_metadata()
        self.assertIn("description", meta)
        self.assertIn("id", meta)
        self.assertIn("name", meta)
        self.assertEqual({}, w.get_train_args())
        self.assertEqual({}, w.get_test_args())

    @mock.patch('deepaas.model.loading.get_available_models')
    def test_loading_ok(self, mock_loading):
        mock_loading.return_value = {uuid.uuid4().hex: "bar"}
        deepaas.model.v1.register_models()
        for m in deepaas.model.v1.MODELS.values():
            self.assertIsInstance(m, deepaas.model.v1.ModelWrapper)

    @mock.patch('deepaas.model.loading.get_available_models')
    def test_loading_error(self, mock_loading):
        mock_loading.return_value = []
        deepaas.model.v1.register_models()
        self.assertIn("deepaas-test", deepaas.model.v1.MODELS)
        m = deepaas.model.v1.MODELS.pop("deepaas-test")
        self.assertIsInstance(m, deepaas.model.v1.ModelWrapper)
        self.assertIsInstance(m.model, deepaas.model.v1.TestModel)
