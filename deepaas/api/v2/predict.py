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

import copy

import flask_restplus
from flask_restplus import fields
import werkzeug
import werkzeug.exceptions as exceptions

from deepaas import model

# Get the models (this is a singleton, so it is safe to call it multiple times
model.register_v2_models()

ns = flask_restplus.Namespace(
    'models',
    description='Model information, inference and training operations')

# This should be removed with marshmallow whenever flask-restplus is ready
data_parser = ns.parser()

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


prediction_links = ns.model('PredictionLinks', {
    "link": fields.String(required=True,
                          description="Link name"),

    "url": fields.String(required=True,
                         description="Link URL"),
})

prediction_info = ns.model('PredictionInfo', {
    "info": fields.String(required=False,
                          description="Prediction Information"),
    "links": fields.List(fields.Nested(prediction_links),
                         required=False)
})

label_prediction = ns.model('LabelPrediction', {
    'label_id': fields.String(required=False, description='Label identifier'),
    'label': fields.String(required=True, description='Class label'),
    'probability': fields.Float(required=True),
    'info': fields.Nested(prediction_info),
})

response = ns.model('ModelResponse', {
    'status': fields.String(required=True,
                            description='Response status message'),
    'predictions': fields.List(fields.Nested(label_prediction),
                               description='Predicted labels and '
                                           'probabilities')
})

# It is better to create different routes for different models instead of using
# the Flask pluggable views. Different models may require different parameters,
# therefore we need to do like this.
#
# Therefore, in the next lines we iterate over the loaded models and create
# the different resources for each model. This way we can also load the
# expected parameters if needed (as in the training method).
for model_name, model_obj in model.V2_MODELS.items():
    # Fill the test parser with the supported arguments. Different models may
    # have different arguments. We get here a copy of the original parser,
    # since otherwise if we have several models the arguments will pile up.
    test_parser = copy.deepcopy(data_parser)
    test_args = model_obj.get_test_args()
    for k, v in test_args.items():
        test_parser.add_argument(k, **v)

    @ns.marshal_with(response, envelope='resource')
    @ns.route('/%s/predict' % model_name)
    class ModelPredict(flask_restplus.Resource):
        model_name = model_name
        model_obj = model_obj
        test_parser = test_parser

        @ns.expect(test_parser)
        def post(self):
            """Make a prediction given the input data."""

            args = self.test_parser.parse_args()

            if (not any([args["urls"], args["files"]]) or
                    all([args["urls"], args["files"]])):
                raise exceptions.BadRequest("You must provide either 'url' or "
                                            "'data' in the payload")

            if args["files"]:
                # FIXME(aloga): only handling one file, see comment on top of
                # file and [1] for more details
                # [1] https://github.com/noirbizarre/flask-restplus/issues/491
                args["files"] = [args["files"]]

                ret = self.model_obj.predict_data(args)
            elif args["urls"]:
                ret = self.model_obj.predict_url(args)
            return ret
