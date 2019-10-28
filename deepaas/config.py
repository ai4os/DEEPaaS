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

import logging
import warnings

from oslo_config import cfg
from oslo_log import log

import deepaas

logging.captureWarnings(True)
warnings.simplefilter("default", DeprecationWarning)

opts = [
    cfg.BoolOpt('enable-v1',
                default="False",
                help="""
Whether to enable V1 version of the API or not.

If this option is set to True, DEEPaaS API will offer a /v1/ endpoing with
the DEPRECATED version of the API.
"""),
    cfg.BoolOpt('debug-endpoint',
                default="false",
                help="""
Enable debug endpoint. If set we will provide all the information that you
print to the standard output and error (i.e. stdout and stderr) through the
"/debug" endpoint. Default is to not provide this information. This will not
provide logging information about the API itself.
"""),
]

CONF = cfg.CONF
CONF.register_cli_opts(opts)


def prepare_logging():
    log.register_options(cfg.CONF)
    log.set_defaults(default_log_levels=log.get_default_log_levels())


def parse_args(argv, default_config_files=None):
    cfg.CONF(argv[1:],
             project='deepaas',
             version=deepaas.__version__,
             default_config_files=default_config_files)


def config_and_logging(argv, default_config_files=None):
    prepare_logging()
    parse_args(argv, default_config_files=default_config_files)
    log.setup(cfg.CONF, "deepaas")
