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
import io
import logging
import sys
import warnings

import fastapi
from oslo_config import cfg

from deepaas import log

CONF = cfg.CONF

router = fastapi.APIRouter(prefix="/debug")


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

    def isatty(self):
        return all(f.isatty() for f in self.handles)


def setup_debug():
    global DEBUG_STREAM

    if CONF.debug_endpoint:
        DEBUG_STREAM = io.StringIO()

        logger = log.getLogger("deepaas")
        hdlr = logging.StreamHandler(DEBUG_STREAM)
        hdlr.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        logger.addHandler(hdlr)

        msg = (
            "\033[0;31;40m WARNING: Running API with debug endpoint! "
            "This will provide ALL the output without any kind of "
            "restriction in the /debug/ endpoint. Disable it whenever "
            "you have finished debugging your application. \033[0m"
        )
        warnings.warn(msg, RuntimeWarning, stacklevel=2)

        sys.stdout = MultiOut(DEBUG_STREAM, sys.stdout)
        sys.stderr = MultiOut(DEBUG_STREAM, sys.stderr)


@router.get(
    "/",
    summary="Return debug information if enabled by API.",
    description="Return debug information if enabled by API.",
    tags=["debug"],
    response_class=fastapi.responses.PlainTextResponse,
    responses={
        "200": {
            "content": {"text/plain": {}},
            "description": "Debug information if debug endpoint is enabled",
        },
        "204": {"description": "Debug endpoint not enabled"},
    },
)
async def get():
    if DEBUG_STREAM is not None:
        print("--- DEBUG MARKER %s ---" % datetime.datetime.now())
        resp = DEBUG_STREAM.getvalue()
        return fastapi.responses.PlainTextResponse(resp)
    else:
        return fastapi.responses.Response(status_code=204)


def get_router() -> fastapi.APIRouter:
    """Auxiliary function to get the router.

    We use this function to be able to include the router in the main
    application and do things before it gets included.
    """
    return router
