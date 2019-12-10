#!/usr/bin/env python
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

import os
import sys

from aiohttp import web
from oslo_config import cfg
from oslo_log import log as oslo_log

import deepaas
from deepaas import api
from deepaas.cmd import _shutdown
from deepaas import config
from deepaas.openwhisk import proxy

cli_opts = [
    cfg.StrOpt('listen-ip',
               default='127.0.0.1',
               help="""
IP address on which the DEEPaaS API will listen.

The DEEPaaS API service listens on this IP address for incoming
requests.
"""),
    cfg.PortOpt('listen-port',
                default=5000,
                help="""
Port on which the DEEPaaS API will listen.

The DEEPaaS API service listens on this port number for incoming
requests.
"""),
    cfg.BoolOpt('openwhisk-detect',
                short='w',
                default=False,
                help="""
Run as an OpenWhisk action.

If this option is set to True DEEPaaS will check if the __OW_API_HOST
environment variable is set. If it is set, it will run an OpenWhisk Docker
action listener rather than the DEEPaaS API. If it is not set, it will run
a DEEPaaS in normal mode.

If you specify this option, the value of 'listen-ip' will be used, but the
port will is hardcoded to 8080 (as OpenWhisk goes to port 8080). Note that
if you are running inside a container, the most sensible option is to set
listen-ip to 0.0.0.0
"""),
]

CONF = cfg.CONF
CONF.register_cli_opts(cli_opts)

INTRO = """
         ##         ###
         ##       ######  ##
     .#####   #####   #######.  .#####.
    ##   ## ## //   ##  //  ##  ##   ##
    ##. .##  ###  ###   // ###  ##   ##
      ## ##    ####     ####    #####.
              Hybrid-DataCloud  ##
"""

BANNER = """
Welcome to the DEEPaaS API API endpoint. You can directly browse to the
API documentation endpoint to check the API using the builtint Swagger UI
or you can use any of our endpoints.

    API documentation: {}
    API specification: {}
          V2 endpoint: {}

-------------------------------------------------------------------------
"""


def main():
    _shutdown.handle_signals()

    config.config_and_logging(sys.argv)
    log = oslo_log.getLogger("deepaas")

    if CONF.openwhisk_detect and os.environ.get('__OW_API_HOST', None):
        log.info("Starting DEEPaaS (OpenWhisk) version %s",
                 deepaas.__version__)

        proxy.main()
    else:
        base = "http://{}:{}".format(CONF.listen_ip, CONF.listen_port)
        spec = "{}/swagger.json".format(base)
        docs = "{}/ui".format(base)
        v2 = "{}/v2".format(base)

        print(INTRO)
        print(BANNER.format(docs, spec, v2))

        log.info("Starting DEEPaaS version %s", deepaas.__version__)

        app = api.get_app(doc="/ui")
        web.run_app(
            app,
            host=CONF.listen_ip,
            port=CONF.listen_port,
        )


if __name__ == "__main__":
    main()
