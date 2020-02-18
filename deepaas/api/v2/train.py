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

import asyncio
import datetime
import uuid

from aiohttp import web
import aiohttp_apispec
from oslo_log import log
from webargs import aiohttpparser
import webargs.core

from deepaas.api.v2 import responses
from deepaas.api.v2 import utils
from deepaas import model

LOG = log.getLogger("deepaas.api.v2.train")


def _get_handler(model_name, model_obj):  # noqa
    args = webargs.core.dict2schema(model_obj.get_train_args())
    args.opts.ordered = True

    class Handler(object):
        model_name = None
        model_obj = None

        def __init__(self, model_name, model_obj):
            self.model_name = model_name
            self.model_obj = model_obj
            self._trainings = {}

        @staticmethod
        def build_train_response(uuid, training):
            if not training:
                return

            ret = {}
            ret["date"] = training["date"]
            ret["uuid"] = uuid

            if training["task"].cancelled():
                ret["status"] = "cancelled"
            elif training["task"].done():
                exc = training["task"].exception()
                if exc:
                    ret["status"] = "error"
                    ret["message"] = "%s" % exc
                else:
                    ret["status"] = "done"
            else:
                ret["status"] = "running"
            return ret

        @aiohttp_apispec.docs(
            tags=["models"],
            summary="Retrain model with available data"
        )
        @aiohttp_apispec.querystring_schema(args)
        @aiohttpparser.parser.use_args(args)
        async def post(self, request, args, wsk_args=None):
            uuid_ = uuid.uuid4().hex
            train_task = self.model_obj.train(**args)
            self._trainings[uuid_] = {
                "date": str(datetime.datetime.now()),
                "task": train_task,
            }
            ret = self.build_train_response(uuid_, self._trainings[uuid_])
            return web.json_response(ret)

        @aiohttp_apispec.docs(
            tags=["models"],
            summary="Cancel a running training"
        )
        async def delete(self, request, wsk_args=None):
            uuid_ = request.match_info["uuid"]
            training = self._trainings.pop(uuid_, None)
            if not training:
                raise web.HTTPNotFound()
            training["task"].cancel()
            try:
                await asyncio.wait_for(training["task"], 5)
            except asyncio.TimeoutError:
                pass
            LOG.info("Training %s has been cancelled" % uuid_)
            ret = self.build_train_response(uuid_, training)
            return web.json_response(ret)

        @aiohttp_apispec.docs(
            tags=["models"],
            summary="Get a list of trainings (running or completed)"
        )
        @aiohttp_apispec.response_schema(responses.TrainingList(), 200)
        async def index(self, request, wsk_args=None):
            ret = []
            for uuid_, training in self._trainings.items():
                training = self._trainings.get(uuid_, None)
                aux = self.build_train_response(uuid_, training)
                ret.append(aux)

            return web.json_response(ret)

        @aiohttp_apispec.docs(
            tags=["models"],
            summary="Get status of a training"
        )
        @aiohttp_apispec.response_schema(responses.Training(), 200)
        async def get(self, request, wsk_args=None):
            uuid_ = request.match_info["uuid"]
            training = self._trainings.get(uuid_, None)
            ret = self.build_train_response(uuid_, training)
            if ret:
                return web.json_response(ret)
            raise web.HTTPNotFound()

    return Handler(model_name, model_obj)


def setup_routes(app, enable=True):
    # In the next lines we iterate over the loaded models and create the
    # different resources for each model. This way we can also load the
    # expected parameters if needed (as in the training method).
    for model_name, model_obj in model.V2_MODELS.items():
        if enable:
            hdlr = _get_handler(model_name, model_obj)
        else:
            hdlr = utils.NotEnabledHandler()
        app.router.add_post(
            "/models/%s/train/" % model_name,
            hdlr.post
        )
        app.router.add_get(
            "/models/%s/train/" % model_name,
            hdlr.index,
            allow_head=False
        )
        app.router.add_get(
            "/models/%s/train/{uuid}" % model_name,
            hdlr.get,
            allow_head=False
        )
        app.router.add_delete(
            "/models/%s/train/{uuid}" % model_name,
            hdlr.delete
        )
