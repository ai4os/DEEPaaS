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

from deepaas import model

# Get the models (this is a singleton, so it is safe to call it multiple times
model.register_v2_models()

ns = flask_restplus.Namespace(
    'models',
    description='Model information, inference and training operations')


def _get_model_response(model_name, model_obj):
    response_schema = model_obj.response_schema
    response_name = "ModelResponse %s" % model_name

    if response_schema is not None:
        return ns.schema_model(response_name, response_schema)

    response = ns.model(response_name, {
        'status': fields.String(required=True,
                                description='Response status message'),
        'predictions': fields.String(
            required=True,
            description='String containing predictions'
        )
    })
    return response


failure = ns.model('Failure', {
    "message": fields.String(required=True,
                             description="Failure message"),
})

# It is better to create different routes for different models instead of using
# the Flask pluggable views. Different models may require different parameters,
# therefore we need to do like this.
#
# Therefore, in the next lines we iterate over the loaded models and create
# the different resources for each model. This way we can also load the
# expected parameters if needed (as in the training method).
for model_name, model_obj in model.V2_MODELS.items():

    response = _get_model_response(model_name, model_obj)

    @ns.route('/%s/predict' % model_name)
    class ModelPredict(flask_restplus.Resource):
        model_name = model_name
        model_obj = model_obj
        parser = model_obj.add_predict_args(ns.parser())

        @ns.response(400, "Bad request", model=failure)
        @ns.response(200, "Sucess", model=response)
        @ns.expect(parser)
        def post(self):
            """Make a prediction given the input data."""

            args = self.parser.parse_args()

            ret = self.model_obj.predict(**args)

            if self.model_obj.has_schema:
                self.model_obj.validate_response(ret)
                return ret

            return {"status": "OK",
                    "predictions": ret}
