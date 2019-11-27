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

from aiohttp import web
import aiohttp_apispec
import marshmallow
from marshmallow import fields
from webargs import aiohttpparser
import webargs.core
import werkzeug.datastructures

from deepaas.api.v2 import responses
from deepaas import model

# Get the models (this is a singleton, so it is safe to call it multiple times
model.register_v1_models()

app = web.Application()
routes = web.RouteTableDef()

APP = None


def get_app():
    global APP

    APP = web.Application()
    APP.router.add_get('/', get_version, name="v1")
    APP.add_routes(routes)

    return APP


@aiohttp_apispec.docs(
    tags=["v1", "versions"],
    summary="Get V1 API version information",
)
@aiohttp_apispec.response_schema(responses.Version(), 200)
@aiohttp_apispec.response_schema(responses.Failure(), 400)
async def get_version(request):
    version = {
        "version": "deprecated",
        "id": "v1",
        "links": [
            {
                "rel": "self",
                # NOTE(aloga): we use our the router table from this
                # application (i.e. the global APP in this module) to be able
                # to build the correct url, as it can be prefixed outside of
                # this module (in an add_subapp() call)
                "href": "%s" % APP.router["v1"].url_for(),
            },
        ]
    }

# NOTE(aloga): skip these for now, until this issue is solved:
# https://github.com/maximdanilchenko/aiohttp-apispec/issues/65
#                doc = "%s.doc" % v.split(".")[0]
#            d = {"rel": "help",
#                 "type": "text/html",
#                 # FIXME(aloga): this -v is wrong
#                 "href": "flask.url_for(doc)"}
#            versions[-1]["links"].append(d)
#
#                specs = "%s.specs" % v.split(".")[0]
#            d = {"rel": "describedby",
#                 "type": "application/json",
#                 # FIXME(aloga): this -v is wrong
#                 "href": "flask.url_for(specs)"}
#            versions[-1]["links"].append(d)

    return web.json_response(version)


@aiohttp_apispec.docs(
    tags=["v1", "v1.models"],
    summary="Return loaded models and its information",
    description="DEEPaaS can load several models and server them on the same "
                "endpoint, making a call to the root of the models namespace "
                "will return the loaded models, as long as their basic "
                "metadata.",
)
@routes.get('/models')
@aiohttp_apispec.response_schema(responses.ModelMeta(), 200)
async def get(request):
    models = []
    for name, obj in model.V1_MODELS.items():
        m = {
            "id": name,
            "name": name,
            "links": [{
                "rel": "self",
                "href": "%s/%s" % (request.path, name),

            }]
        }
        meta = obj.get_metadata()
        m.update(meta)
        models.append(m)
    return web.json_response({"models": models})


class PredictionLinks(marshmallow.Schema):
    link = fields.Str(required=True,
                      description="Link name")

    url = fields.Str(required=True,
                     description="Link URL")


class PredictionInfo(marshmallow.Schema):
    links = fields.Nested(PredictionLinks)
    info = fields.Str(required=False,
                      description="Prediction Information")


class LabelPrediction(marshmallow.Schema):
    label_id = fields.Str(required=False, description='Label identifier')
    label = fields.Str(required=True, description='Class label')
    probability = fields.Float(required=True)
    info = fields.Nested(PredictionInfo)


class ModelResponse(marshmallow.Schema):
    status = fields.Str(required=True,
                        description='Response status message')
    predictions = fields.List(fields.Nested(LabelPrediction),
                              description='Predicted labels and probabilities')


# It is better to create different routes for different models instead of using
# the Flask pluggable views. Different models may require different parameters,
# therefore we need to do like this.
#
# Therefore, in the next lines we iterate over the loaded models and create
# the different resources for each model. This way we can also load the
# expected parameters if needed (as in the training method).
for model_name, model_obj in model.V1_MODELS.items():
    @routes.view('/models/%s' % model_name)
    class BaseModel(web.View):
        model_name = model_name
        model_obj = model_obj

        @aiohttp_apispec.docs(
            tags=["v1", "v1.models"],
            summary="Return '%s' model metadata" % model_name,
        )
        @aiohttp_apispec.response_schema(responses.ModelMeta(), 200)
        async def get(self):
            """Return model's metadata."""

            m = {
                "id": self.model_name,
                "name": self.model_name,
                "links": [{
                    "rel": "self",
                    "href": "%s" % self.request.path,
                }]
            }
            meta = self.model_obj.get_metadata()
            m.update(meta)
            return web.json_response(m)

    # Fill the test parser with the supported arguments. Different models may
    # have different arguments. We get here a copy of the original parser,
    # since otherwise if we have several models the arguments will pile up.
    test_args = model_obj.get_test_args()
    args = {
        "url": fields.List(fields.Str()),
        "data": fields.Field(
            description="Data file to perform inference.",
            location="form",
            type="file",
        ),
    }
    for k, v in test_args.items():
        args[k] = fields.Str(
            description=v.get("help"),
            required=v.get("required"),
            default=v.get("default")
        )
    args = webargs.core.dict2schema(args)
    args.opts.ordered = True

    @routes.view('/models/%s/predict' % model_name)
    class ModelPredict(web.View):
        model_name = model_name
        model_obj = model_obj

        @aiohttp_apispec.docs(
            tags=["v1", "v1.models"],
            summary="Make a prediction given the input data",
            responses={
                501: {"description": "Functionality not implemented"},
            }
        )
        @aiohttp_apispec.querystring_schema(args)
        @aiohttp_apispec.response_schema(ModelResponse(), 200)
        @aiohttp_apispec.response_schema(responses.Failure(), 400)
        @aiohttpparser.parser.use_args(args)
        async def post(self, args):
            """Make a prediction given the input data."""

            urls = args.get("url")
            files = args.get("data")
            if (not any([urls, files]) or all([urls, files])):
                raise web.HTTPBadRequest(
                    reason="You must provide either 'url' or "
                    "'data' in the payload"
                )

            args["urls"] = urls

            if files:
                # FIXME(aloga): only handling one file, see comment on top of
                # file and [1] for more details
                # [1] https://github.com/noirbizarre/flask-restplus/issues/491
                tmp = werkzeug.datastructures.FileStorage(
                    stream=files.file,
                    filename=files.filename
                )
                args["files"] = [tmp]

                ret = self.model_obj.predict_data(args)
            elif urls:
                ret = self.model_obj.predict_url(args)
            return web.json_response(ret)

    # Fill the train parser with the supported arguments. Different models may
    # have different arguments.
    train_args = model_obj.get_train_args()
    args = {}
    for k, v in train_args.items():
        args[k] = fields.Str(
            description=v.get("help"),
            required=v.get("required"),
            default=v.get("default")
        )
    args = webargs.core.dict2schema(args)
    args.opts.ordered = True

    @routes.view('/models/%s/train' % model_name)
    class ModelTrain(web.View):
        model_name = model_name
        model_obj = model_obj

        @aiohttp_apispec.docs(
            tags=["v1", "v1.models"],
            summary="Retrain model with available data",
            responses={
                501: {"description": "Functionality not implemented"},
            }
        )
        @aiohttp_apispec.querystring_schema(args)
        @aiohttpparser.parser.use_args(args)
        async def put(self, args):
            ret = self.model_obj.train(args)
            # FIXME(aloga): what are we returning here? We need to marshal the
            # response!!
            return web.json_response(ret)
