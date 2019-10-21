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

import flask
import flask_restplus.model
import six

import deepaas
from deepaas.api import v2
from deepaas.api.v2 import predict
import deepaas.model
import deepaas.model.v2
from deepaas.tests import base


class TestModelResponse(base.TestCase):
    def test_loading_ok_with_missing_schema(self):
        class Fake(object):
            response_schema = None
        response = predict._get_model_response("deepaas-test", Fake)
        self.assertIsInstance(response, flask_restplus.model.Model)


class TestApiV2(base.TestCase):
    def setUp(self):
        super(TestApiV2, self).setUp()

        app = flask.Flask(__name__)
        app.config['TESTING'] = True
        app.config['DEBUG'] = True

        self.maxDiff = None

        self.flags(debug=True)
        deepaas.model.v2.register_models()

        bp = v2.get_blueprint()
        app.register_blueprint(bp)

        self.app = app.test_client()
        self.assertEqual(app.debug, True)

    def assert_ok(self, response):
        self.assertIn(response.status_code, [200, 201])

    def test_not_found(self):
        ret = self.app.get("/v2/models/%s" % uuid.uuid4().hex)
        self.assertEqual(404, ret.status_code)

        ret = self.app.put("/v2/models/%s" % uuid.uuid4().hex)
        self.assertEqual(404, ret.status_code)

        ret = self.app.post("/v2/models/%s" % uuid.uuid4().hex)
        self.assertEqual(404, ret.status_code)

        ret = self.app.delete("/v2/models/%s" % uuid.uuid4().hex)
        self.assertEqual(404, ret.status_code)

    def test_model_not_found(self):
        ret = self.app.put("/v2/models/%s/train" % uuid.uuid4().hex)
        self.assertEqual(404, ret.status_code)

        ret = self.app.post("/v2/models/%s/predict" % uuid.uuid4().hex)
        self.assertEqual(404, ret.status_code)

        ret = self.app.get("/v2/models/%s" % uuid.uuid4().hex)
        self.assertEqual(404, ret.status_code)

#    def test_train_not_implemented(self):
#        ret = self.app.put("/v2/models/not-implemented/train")
#        self.assertEqual(501, ret.status_code)
#
    def test_predict_no_parameters(self):
        ret = self.app.post("/v2/models/deepaas-test/predict")
        self.assertIn("Input payload validation failed", ret.json["message"])
        self.assertEqual(400, ret.status_code)

    def test_predict_data(self):
        f = six.BytesIO(b"foo")
        ret = self.app.post(
            "/v2/models/deepaas-test/predict",
            data={"data": (f, "foo.txt"),
                  "parameter": 1})
        self.assertEqual(200, ret.status_code)

    def test_train(self):
        ret = self.app.put("/v2/models/deepaas-test/train",
                           data={"parameter_one": 1})
        self.assertEqual(200, ret.status_code)

    def test_get_metadata(self):
        meta = {'models': [
            {'author': 'Alvaro Lopez Garcia',
             'description': ('This is not a model at all, just a '
                             'placeholder for testing the API '
                             'functionality. If you are seeing this, it is '
                             'because DEEPaaS could not load a valid model.'),
             'id': '0',
             'links': [{'href': '/v2/models/deepaas-test', 'rel': 'self'}],
             'name': 'deepaas-test',
             'url': "https://github.com/indigo-dc/DEEPaaS/",
             'license': "Apache 2.0",
             'version': '0.0.1'}
        ]}

        ret = self.app.get("/v2/models/")
        self.assert_ok(ret)
        self.assertDictEqual(meta, ret.json)

        ret = self.app.get("/v2/models/deepaas-test")
        self.assert_ok(ret)
        self.assertDictEqual(meta["models"][0], ret.json)

    def test_bad_metods_metadata(self):
        for i in (self.app.post, self.app.put, self.app.delete):
            ret = i("/v2/models/")
            self.assertEqual(405, ret.status_code)
