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

from deepaas import model

# Get the models (this is a singleton, so it is safe to call it multiple times
model.register_v2_models()

ns = flask_restplus.Namespace(
    'models',
    description='Model information, inference and training operations')

# It is better to create different routes for different models instead of using
# the Flask pluggable views. Different models may require different parameters,
# therefore we need to do like this.
#
# Therefore, in the next lines we iterate over the loaded models and create
# the different resources for each model. This way we can also load the
# expected parameters if needed (as in the training method).
for model_name, model_obj in model.V2_MODELS.items():
    @ns.route('/%s/train' % model_name)
    class ModelTrain(flask_restplus.Resource):
        model_name = model_name
        model_obj = model_obj
        parser = model_obj.add_train_args(ns.parser())

        @ns.doc('Retrain model')
        @ns.expect(parser)
        def put(self):
            """Retrain model with available data."""

            args = self.parser.parse_args()
            ret = self.model_obj.train(**args)
            # FIXME(aloga): what are we returning here? We need to take care
            # of these responses as well.
            return ret
