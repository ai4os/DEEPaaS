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

import deepaas

api = flask_restplus.Namespace(
    'model',
    description='Model information, inference and training operations')

# This should be removed with marshmallow whenever flask-restplus is ready
data_parser = api.parser()
data_parser.add_argument('data',
                         help="Data file to perform inference.",
                         type=werkzeug.FileStorage,
                         location='files',
                         dest='files',
                         required=True)

# data_parser.add_argument('url',
#                          help="URL to retrieve data to perform inference.",
#                          type=str,
#                          dest='urls',
#                          required=False,
#                          action="append")

model_meta = api.model('ModelMetadata', {
    'id': fields.String(required=True, description='Model identifier'),
    'name': fields.String(required=True, description='Model name'),
    'description': fields.String(required=True,
                                 description='Model description'),
    'license': fields.String(required=False, description='Model license'),
    'author': fields.String(required=False, description='Model author'),
    'version': fields.String(required=False, description='Model version'),
    'url': fields.String(required=False, description='Model url'),
})


prediction_links = api.model('PredictionLinks', {
    "link": fields.String(required=True,
                          description="Link name"),

    "url": fields.String(required=True,
                         description="Link URL"),
})

prediction_info = api.model('PredictionInfo', {
    "info": fields.String(required=False,
                          description="Prediction Information"),
    "links": fields.List(fields.Nested(prediction_links),
                         required=False)
})

label_prediction = api.model('LabelPrediction', {
    'label_id': fields.String(required=False, description='Label identifier'),
    'label': fields.String(required=True, description='Class label'),
    'probability': fields.Float(required=True),
    'info': fields.Nested(prediction_info),
})

response = api.model('ModelResponse', {
    'status': fields.String(required=True,
                            description='Response status message'),
    'predictions': fields.List(fields.Nested(label_prediction),
                               description='Predicted labels and '
                                           'probabilities')
})


@api.marshal_with(model_meta, envelope='resource')
@api.route('/')
class BaseModel(flask_restplus.Resource):
    def get(self):
        """Return model information."""
        r = {
            "id": "0",
            "name": "Not a model",
            "description": "Placeholder metadata, model not implemented",
            "author": "Alvaro Lopez Garcia",
            "version": deepaas.__version__,
        }
        return r
        raise exceptions.NotImplemented()


@api.marshal_with(response, envelope='resource')
@api.route('/predict')
class ModelPredict(flask_restplus.Resource):
    @api.expect(data_parser)
    def post(self):
        """Make a prediction given the input data."""

        args = data_parser.parse_args()

#        if not any([args["urls"], args["files"]]):
#            raise exceptions.BadRequest("You must provide either 'url' or "
#                                        "'data' in the payload")

        raise exceptions.NotImplemented("Not implemented by underlying model")


@api.route('/train')
class ModelTrain(flask_restplus.Resource):
    @api.doc('Retrain model')
    def put(self):
        """Retrain model with available data."""

        raise exceptions.NotImplemented("Not implemented by underlying model")
