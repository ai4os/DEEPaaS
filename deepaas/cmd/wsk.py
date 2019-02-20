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
from deepaas import config
from deepaas.openwisk import proxy

cli_opts = [
    cfg.StrOpt('listen-ip',
               default='127.0.0.1',
               help="""
IP address on which the DEEPaaS API will listen.

The DEEPaaS API service listens on this IP address for incoming
requests.
"""),
]

CONF = cfg.CONF
CONF.register_cli_opts(cli_opts)


def main():
    config.parse_args(sys.argv)
    logging.setup(CONF, "deepaas")
    log = logging.getLogger(__name__)

    log.info("Starting DEEPaaS (OpenWhisk) version %s", deepaas.__version__)

    proxy.main()


if __name__ == "__main__":
    main()
