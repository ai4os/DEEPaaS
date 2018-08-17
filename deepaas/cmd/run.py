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

import sys

from oslo_config import cfg
from oslo_log import log as logging

import deepaas
from deepaas import api
from deepaas import config

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
]

CONF = cfg.CONF
CONF.register_cli_opts(cli_opts)


def main():
    config.parse_args(sys.argv)
    logging.setup(CONF, "deepaas")
    log = logging.getLogger(__name__)

    log.info("Starting DEEPaaS version %s", deepaas.__version__)

    app = api.get_app()
    app.run(
        host=CONF.listen_ip,
        port=CONF.listen_port,
        debug=CONF.debug,
    )


if __name__ == "__main__":
    main()
