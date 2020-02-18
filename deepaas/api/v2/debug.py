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

import datetime
import logging
import sys
import warnings

from aiohttp import web
import aiohttp_apispec
from oslo_config import cfg
from oslo_log import log
import six

CONF = cfg.CONF

app = web.Application()
routes = web.RouteTableDef()

# Ugly global variable to provide a string stream to read the DEBUG output
# if it is enabled
DEBUG_STREAM = None


class MultiOut(object):
    def __init__(self, *args):
        self.handles = args

    def write(self, s):
        for f in self.handles:
            f.write(s)

    def flush(self):
        for f in self.handles:
            f.flush()

    def close(self):
        for f in self.handles:
            f.close()


def setup_debug():
    global DEBUG_STREAM

    if CONF.debug_endpoint:
        DEBUG_STREAM = six.StringIO()

        logger = log.getLogger("deepaas").logger
        hdlr = logging.StreamHandler(DEBUG_STREAM)
        hdlr.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        logger.addHandler(hdlr)

        msg = ("\033[0;31;40m WARNING: Running API with debug endpoint! "
               "This will provide ALL the output without any kind of "
               "restriction in the /debug/ endpoint. Disable it whenever "
               "you have finished debugging your application. \033[0m")
        warnings.warn(msg, RuntimeWarning)

        sys.stdout = MultiOut(DEBUG_STREAM, sys.stdout)
        sys.stderr = MultiOut(DEBUG_STREAM, sys.stderr)


@aiohttp_apispec.docs(
    tags=["debug"],
    summary="""Return debug information if enabled by API.""",
    description="""Return debug information if enabled by API.""",
    produces=["text/plain"],
    responses={
        200: {"description": "Debug information if debug endpoint is enabled"},
        204: {"description": "Debug endpoint not enabled"},
    },
)
async def get(request, wsk_args=None):
    if DEBUG_STREAM is not None:
        print("--- DEBUG MARKER %s ---" % datetime.datetime.now())
        resp = DEBUG_STREAM.getvalue()
        return web.Response(text=resp)
    return web.HTTPNoContent()


def setup_routes(app):
    app.router.add_get(
        "/debug/",
        get,
        allow_head=False
    )
