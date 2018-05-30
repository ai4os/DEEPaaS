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

import flask
import flask_restplus
import mock
import six

import deepaas
from deepaas import api
from deepaas.api import v1
import deepaas.model
from deepaas.tests import base


class TestApi(base.TestCase):
    @mock.patch('deepaas.api.app')
    def test_get_app(self, mock_app):
        self.assertEqual(mock_app, api.get_app())

    @mock.patch('deepaas.loading.get_available_model_names')
    @mock.patch('deepaas.api.app')
    def test_loading_ok(self, mock_app, mock_loading):
        self.assertEqual(mock_app, api.get_app())
        mock_loading.assert_called_once()

    @mock.patch('deepaas.loading.get_available_model_names')
    @mock.patch('deepaas.api.app')
    def test_loading_ok_with_model(self, mock_app, mock_loading):
        mock_loading.return_value = ["foo"]
        self.assertEqual(mock_app, api.get_app())
        mock_loading.assert_called_once()


class TestApiV1(base.TestCase):
    def setUp(self):
        super(TestApiV1, self).setUp()

        app = flask.Flask(__name__)
        app.config['TESTING'] = True
        app.config['DEBUG'] = True

        api = flask_restplus.Api(app, doc=False)
        api.add_namespace(v1.api)

        self.app = app.test_client()
        self.assertEqual(app.debug, True)

    def assert_ok(self, response):
        self.assertIn(response.status_code, [200, 201])

    def test_train(self):
        ret = self.app.put("/model/train")
        self.assertEqual(501, ret.status_code)

    def test_predict_not_data(self):
        ret = self.app.post("/model/predict")
        self.assertEqual(400, ret.status_code)

    def test_predict_data_not_implemented(self):
        f = six.BytesIO(b"foo")
        ret = self.app.post(
            "/model/predict",
            data={"data": (f, "foo.txt")})
        self.assertEqual(501, ret.status_code)

    def test_predict_with_model(self):
        m = mock.Mock()
        m.return_value = {}
        content = b"foo"
        f = six.BytesIO(b"foo")
        with mock.patch.object(deepaas.model, "MODEL", ("fake", m)):
            ret = self.app.post(
                "/model/predict",
                data={"data": (f, "foo.txt")})
            m.assert_called_with([content])
            self.assertEqual(200, ret.status_code)
            self.assertEqual({}, ret.json)

    def test_get_metadata(self):
        meta = {
            "description": "Placeholder metadata, model not implemented",
            "author": "Alvaro Lopez Garcia",
            "id": "0",
            "version": deepaas.__version__,
            "name": "Not a model"
        }
        ret = self.app.get("/model/")
        self.assert_ok(ret)
        self.assertDictEqual(meta, ret.json)

    def test_bad_metods_metadata(self):
        for i in (self.app.post, self.app.put, self.app.delete):
            ret = i("/model/")
            self.assertEqual(405, ret.status_code)
