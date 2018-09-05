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

import mock
import werkzeug.exceptions as exceptions

import deepaas
import deepaas.model
from deepaas.tests import base


class TestModel(base.TestCase):
    def test_abc(self):
        self.assertRaises(TypeError, deepaas.model.BaseModel)

    def test_dummy_model(self):
        m = deepaas.model.TestModel()
        for meth in (m.predict_file, m.predict_url, m.predict_data):
            self.assertRaises(NotImplementedError, meth, None)
        self.assertRaises(NotImplementedError, m.train)
        meta = m.get_metadata()
        self.assertIn("description", meta)
        self.assertIn("id", meta)
        self.assertIn("name", meta)
        self.assertEqual("Alvaro Lopez Garcia", meta["author"])

    def test_dummy_model_with_wrapper(self):
        w = deepaas.model.ModelWrapper("foo", deepaas.model.TestModel())
        for meth in (w.predict_file, w.predict_url, w.predict_data):
            self.assertRaises(exceptions.NotImplemented, meth, None)
        self.assertRaises(exceptions.NotImplemented, w.train)
        meta = w.get_metadata()
        self.assertIn("description", meta)
        self.assertIn("id", meta)
        self.assertIn("name", meta)

    def test_model_with_not_implemented_attributes_and_wrapper(self):
        w = deepaas.model.ModelWrapper("foo", object())
        for meth in (w.predict_file, w.predict_url, w.predict_data):
            self.assertRaises(exceptions.NotImplemented, meth, None)
        self.assertRaises(exceptions.NotImplemented, w.train)
        meta = w.get_metadata()
        self.assertIn("description", meta)
        self.assertIn("id", meta)
        self.assertIn("name", meta)

    @mock.patch('deepaas.loading.get_available_models')
    def test_loading_ok(self, mock_loading):
        mock_loading.return_value = {uuid.uuid4().hex: "bar"}
        deepaas.model.register_models()
        for m in deepaas.model.MODELS.values():
            self.assertIsInstance(m, deepaas.model.ModelWrapper)

    @mock.patch('deepaas.loading.get_available_models')
    def test_loading_error(self, mock_loading):
        mock_loading.return_value = []
        deepaas.model.register_models()
        self.assertIn("deepaas-test", deepaas.model.MODELS)
        m = deepaas.model.MODELS.pop("deepaas-test")
        self.assertIsInstance(m, deepaas.model.ModelWrapper)
        self.assertIsInstance(m.model, deepaas.model.TestModel)
