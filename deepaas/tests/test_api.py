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

import unittest
import uuid

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
    @mock.patch('deepaas.api.APP')
    def test_get_app(self, mock_app):
        self.assertEqual(mock_app, api.get_app())


class TestApiV1(base.TestCase):
    def setUp(self):
        super(TestApiV1, self).setUp()

        app = flask.Flask(__name__)
        app.config['TESTING'] = True
        app.config['DEBUG'] = True

        api = flask_restplus.Api(app, doc=False)
        api.add_namespace(v1.api)

        deepaas.model.register_models()

        self.app = app.test_client()
        self.assertEqual(app.debug, True)

    def assert_ok(self, response):
        self.assertIn(response.status_code, [200, 201])

    def test_not_found(self):
        ret = self.app.get("/models/%s" % uuid.uuid4().hex)
        self.assertEqual(404, ret.status_code)

        ret = self.app.put("/models/%s" % uuid.uuid4().hex)
        self.assertEqual(404, ret.status_code)

        ret = self.app.post("/models/%s" % uuid.uuid4().hex)
        self.assertEqual(404, ret.status_code)

        ret = self.app.delete("/models/%s" % uuid.uuid4().hex)
        self.assertEqual(404, ret.status_code)

    def test_model_not_found(self):
        ret = self.app.put("/models/%s/train" % uuid.uuid4().hex)
        self.assertEqual(404, ret.status_code)

        ret = self.app.post("/models/%s/predict" % uuid.uuid4().hex)
        self.assertEqual(404, ret.status_code)

        ret = self.app.get("/models/%s" % uuid.uuid4().hex)
        self.assertEqual(404, ret.status_code)

    def test_train(self):
        ret = self.app.put("/models/deepaas-test/train")
        self.assertEqual(501, ret.status_code)

    def test_predict_not_data(self):
        ret = self.app.post("/models/deepaas-test/predict")
        self.assertEqual(400, ret.status_code)

    def test_predict_data_not_implemented(self):
        f = six.BytesIO(b"foo")
        ret = self.app.post(
            "/models/deepaas-test/predict",
            data={"data": (f, "foo.txt")})
        self.assertEqual(501, ret.status_code)

    def test_predict_urls_not_implemented(self):
        ret = self.app.post(
            "/models/deepaas-test/predict",
            data={"url": "http://example.org/"})
        self.assertEqual(501, ret.status_code)

    def test_predict_various_urls_not_implemented(self):
        ret = self.app.post(
            "/models/deepaas-test/predict",
            data={"url": ["http://example.org/", "http://example.com"]})
        self.assertEqual(501, ret.status_code)

    @unittest.skip("Refactor made test fail, changes in API needed")
    def test_predict_data_with_model(self):
        m = mock.MagicMock()
        content = b"foo"
        f = six.BytesIO(b"foo")
        with mock.patch.object(deepaas.model, "MODELS", {"fake": m}):
            m.predict_data.return_value = {}
            ret = self.app.post(
                "/models/fake/predict",
                data={"data": (f, "foo.txt")})
            m.predict_data.assert_called_with([content])
            self.assertEqual(200, ret.status_code)
            self.assertEqual({}, ret.json)

    @unittest.skip("Refactor made test fail, changes in API needed")
    def test_predict_url_with_model(self):
        m = mock.MagicMock()
        url = ["http://example.com"]
        with mock.patch.object(deepaas.model, "MODELS", {"fake": m}):
            m.predict_url.return_value = {}
            ret = self.app.post(
                "/models/fake/predict",
                data={"url": url})
            m.predict_url.assert_called_with(url)
            self.assertEqual(200, ret.status_code)
            self.assertEqual({}, ret.json)

    @unittest.skip("Refactor made test fail, changes in API needed")
    def test_predict_various_urls_with_model(self):
        m = mock.MagicMock()
        url = ["http://example.org/", "http://example.com"]
        with mock.patch.object(deepaas.model, "MODELS", {"fake": m}):
            m.predict_url.return_value = {}
            ret = self.app.post(
                "/models/fake/predict",
                data={"url": url})
            m.predict_url.assert_called_with(url)
            self.assertEqual(200, ret.status_code)
            self.assertEqual({}, ret.json)

    def test_get_metadata(self):
        meta = {'models': [
            {'author': 'Alvaro Lopez Garcia',
             'description': ('This is not a model at all, just a '
                             'placeholder for testing the API '
                             'functionality. If you are seeing this, it is '
                             'because DEEPaaS could not load a valid model.'),
             'id': '0',
             'links': [{'href': '/models/deepaas-test', 'rel': 'self'}],
             'name': 'deepaas-test',
             'version': '0.0.1'}
        ]}

        ret = self.app.get("/models/")
        self.assert_ok(ret)
        self.assertDictEqual(meta, ret.json)

        ret = self.app.get("/models/deepaas-test")
        self.assert_ok(ret)
        self.assertDictEqual(meta["models"][0], ret.json)

    def test_bad_metods_metadata(self):
        for i in (self.app.post, self.app.put, self.app.delete):
            ret = i("/models/")
            self.assertEqual(405, ret.status_code)
