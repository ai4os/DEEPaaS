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

from deepaas import model

api = flask_restplus.Namespace(
    'models',
    description='Model information, inference and training operations')

# This should be removed with marshmallow whenever flask-restplus is ready
data_parser = api.parser()

# FIXME(aloga): currently we allow only to upload one file. There is a bug in
# the Swagger UI that makes impossible to upload several files, although this
# works if the request is not done through swagger. Since providing a UI and an
# API that behave differently is incoherent, only allow one file for the time
# being.
#
# See https://github.com/noirbizarre/flask-restplus/issues/491 for more details
# on the bug.
data_parser.add_argument('data',
                         help="Data file to perform inference.",
                         type=werkzeug.FileStorage,
                         location="files",
                         dest='files',
                         required=False)

data_parser.add_argument('url',
                         help="URL to retrieve data to perform inference.",
                         type=str,
                         dest='urls',
                         required=False,
                         action="append")

model_links = api.model('Location', {
    "rel": fields.String(required=True),
    "href": fields.Url(required=True)
})

model_meta = api.model('ModelMetadata', {
    'id': fields.String(required=True, description='Model identifier'),
    'name': fields.String(required=True, description='Model name'),
    'description': fields.String(required=True,
                                 description='Model description'),
    'license': fields.String(required=False, description='Model license'),
    'author': fields.String(required=False, description='Model author'),
    'version': fields.String(required=False, description='Model version'),
    'url': fields.Url(required=False, description='Model url'),
    'links': fields.List(fields.Nested(model_links))
})

models = api.model('Models', {
    'models': fields.List(fields.Nested(model_meta)),
})


@api.marshal_with(models, envelope='resource')
@api.route('/')
class Models(flask_restplus.Resource):
    def get(self):
        """Return loaded models and its information.

        DEEPaaS can load several models and server them on the same endpoint,
        making a call to the root of the models namespace will return the
        loaded models, as long as their basic metadata.
        """

        models = []
        for name, obj in model.MODELS.items():
            m = {
                "id": name,
                "name": name,
                "links": [{
                    "rel": "self",
                    "href": "%s%s" % (flask.request.path, name),
                }]
            }
            meta = obj.get_metadata()
            m.update(meta)
            models.append(m)
        return {"models": models}


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
@api.route('/<string:model_name>')
class BaseModel(flask_restplus.Resource):
    def get(self, model_name):
        """Return <model_name> models metadata."""
        if model_name not in model.MODELS:
            raise exceptions.NotFound(description="No model %s is found" %
                                      model_name)

        obj = model.MODELS.get(model_name)

        m = {
            "id": model_name,
            "name": model_name,
            "links": [{
                "rel": "self",
                "href": "%s" % flask.request.path,
            }]
        }
        meta = obj.get_metadata()
        m.update(meta)
        return m


@api.marshal_with(response, envelope='resource')
@api.route('/<string:model_name>/predict')
class ModelPredict(flask_restplus.Resource):
    @api.expect(data_parser)
    def post(self, model_name):
        """Make a prediction given the input data."""
        if model_name not in model.MODELS:
            raise exceptions.NotFound(description="No model %s is found" %
                                      model_name)

        obj = model.MODELS.get(model_name)

        args = data_parser.parse_args()

        if (not any([args["urls"], args["files"]]) or
                all([args["urls"], args["files"]])):
            raise exceptions.BadRequest("You must provide either 'url' or "
                                        "'data' in the payload")

        if args["files"]:
            # FIXME(aloga): only handling one file, see comment on top of file
            # and https://github.com/noirbizarre/flask-restplus/issues/491 for
            # more details
            # data = [f.read() for f in args["files"]]
            data = [args["files"].read()]
            ret = obj.predict_data(data)
        elif args["urls"]:
            ret = obj.predict_url(args["urls"])
        return ret


@api.route('/<string:model_name>/train')
class ModelTrain(flask_restplus.Resource):
    @api.doc('Retrain model')
    def put(self, model_name):
        """Retrain model with available data."""
        if model_name not in model.MODELS:
            raise exceptions.NotFound(description="No model %s is found" %
                                      model_name)

        obj = model.MODELS.get(model_name)
        ret = obj.train()
        return ret
