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

import flask_restplus
from flask_restplus import fields
import werkzeug
import werkzeug.exceptions as exceptions

api = flask_restplus.Namespace(
    'model',
    description='Model information, inference and training operations')

# This should be removed with marshmallow whenever flask-restplus is ready
data_parser = api.parser()
data_parser.add_argument('data',
                         help="Data file to perform inference.",
                         type=werkzeug.FileStorage,
                         location='files',
                         required=False,
                         action="append")

data_parser.add_argument('url',
                         help="URL to retrieve data to perform inference.",
                         type=str,
                         location='urls',
                         required=False,
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


@api.route('/')
class BaseModel(flask_restplus.Resource):
    def get(self):
        """Return model information."""
        raise exceptions.NotImplemented()


@api.marshal_with(response, envelope='resource')
@api.route('/predict')
class ModelPredict(flask_restplus.Resource):
    @api.expect(data_parser)
    def post(self):
        """Make a prediction given the input data."""

        args = data_parser.parse_args()

        if not any([args["url"], args["data"]]):
            raise exceptions.BadRequest("You must provide either 'url' or "
                                        "'data' in the payload")

        raise exceptions.NotImplemented("Not implemented by underlying model")


@api.route('/train')
class ModelTrain(flask_restplus.Resource):
    @api.doc('Retrain model')
    def put(self):
        """Retrain model with available data."""

        raise exceptions.NotImplemented("Not implemented by underlying model")
