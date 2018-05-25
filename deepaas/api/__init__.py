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
from flask_restplus import fields
import werkzeug
import werkzeug.exceptions as exceptions

import deepaas

app = flask.Flask(__name__)
api = flask_restplus.Api(
    app,
    version=deepaas.__version__,
    title='DEEP as a Service API',
    description='Initial DEEP as a Service (DEEPaaS) API.',
)
ns = api.namespace('model',
                   description='Model information and inference operations')

# This should be removed with marshmallow whenever flask-restplus is ready
data_parser = api.parser()
data_parser.add_argument('data',
                         help="Data file to perform inference.",
                         type=werkzeug.FileStorage,
                         location='files',
                         required=True,
                         action="append")

label_prediction = api.model('LabelPrediction', {
    'label_id': fields.String(required=False, description='Label identifier'),
    'label': fields.String(required=True, description='Class label'),
    'probability': fields.Float(required=True)
})

response = api.model('ModelResponse', {
    'status': fields.String(required=True,
                            description='Response status message'),
    'predictions': fields.List(fields.Nested(label_prediction),
                               description='Predicted labels and '
                                           'probabilities')
})


class BaseModel(flask_restplus.Resource):
    def get(self):
        """Return model information."""
        raise exceptions.NotImplemented()


@ns.marshal_with(response, envelope='resource')
@ns.route('/predict')
class ModelPredict(BaseModel):
    def get(self):
        """Return model information."""
        raise exceptions.NotImplemented()

    @ns.expect(data_parser)
    def post(self):
        """Make a prediction given the input data."""

        raise exceptions.NotImplemented("Not implemented by underlying model")


@ns.route('/train')
class ModelTrain(BaseModel):
    def get(self):
        """Return model information."""
        raise exceptions.NotImplemented("Not implemented by underlying model")

    @ns.doc('Retrain model')
    def put(self):
        """Retrain model with available data."""

        raise exceptions.NotImplemented("Not implemented by underlying model")


def get_app():
    return app
