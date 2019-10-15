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

from deepaas import model

# Get the models (this is a singleton, so it is safe to call it multiple times
model.register_v2_models()

ns = flask_restplus.Namespace(
    'models',
    description='Model information, inference and training operations')

model_links = ns.model('Location', {
    "rel": fields.String(required=True),
    "href": fields.Url(required=True)
})

model_meta = ns.model('ModelMetadata', {
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

models = ns.model('Models', {
    'models': fields.List(fields.Nested(model_meta)),
})


@ns.marshal_with(models, envelope='resource')
@ns.route('/')
class Models(flask_restplus.Resource):
    def get(self):
        """Return loaded models and its information.

        DEEPaaS can load several models and server them on the same endpoint,
        making a call to the root of the models namespace will return the
        loaded models, as long as their basic metadata.
        """

        models = []
        for name, obj in model.V2_MODELS.items():
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


# It is better to create different routes for different models instead of using
# the Flask pluggable views. Different models may require different parameters,
# therefore we need to do like this.
#
# Therefore, in the next lines we iterate over the loaded models and create
# the different resources for each model. This way we can also load the
# expected parameters if needed (as in the training method).
for model_name, model_obj in model.V2_MODELS.items():
    @ns.marshal_with(model_meta, envelope='resource')
    @ns.route('/%s' % model_name)
    class BaseModel(flask_restplus.Resource):
        model_name = model_name
        model_obj = model_obj

        def get(self):
            """Return model's metadata."""

            m = {
                "id": self.model_name,
                "name": self.model_name,
                "links": [{
                    "rel": "self",
                    "href": "%s" % flask.request.path,
                }]
            }
            meta = self.model_obj.get_metadata()
            m.update(meta)
            return m
