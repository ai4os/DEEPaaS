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
import os
import warnings

from oslo_config import cfg
from oslo_log import log

import deepaas

logging.captureWarnings(True)
warnings.simplefilter("default", DeprecationWarning)

opts = [
    cfg.BoolOpt(
        "train-endpoint",
        default=True,
        help="""
Specify whether DEEPaaS should provide a train endpoint (default: True).
""",
    ),
    cfg.BoolOpt(
        "predict-endpoint",
        default=True,
        help="""
Specify whether DEEPaaS should provide a predict endpoint (default: True).
""",
    ),
    cfg.BoolOpt(
        "debug-endpoint",
        default=False,
        help="""
Enable debug endpoint. If set we will provide all the information that you
print to the standard output and error (i.e. stdout and stderr) through the
"/debug" endpoint. Default is to not provide this information. This will not
provide logging information about the API itself.
""",
    ),
    cfg.BoolOpt(
        "doc-endpoint",
        default=True,
        help="""
Enable documentation endpoint. If set we will provide the documentation
through the "/api" endpoint. Default is to provide this information.
""",
    ),
    cfg.IntOpt(
        "workers",
        short="p",
        default=1,
        help="""
Specify the number of workers to spawn. If using a CPU you probably want to
increase this number, if using a GPU probably you want to leave it to 1.
(defaults to 1)
""",
    ),
    cfg.IntOpt(
        "client-max-size",
        default=0,
        min=0,
        help="""
Client’s maximum size in a request, in bytes. If a POST request exceeds this
value, it raises an HTTPRequestEntityTooLarge exception. If set to 0, no
file size limit will be enforced.
""",
    ),
    cfg.BoolOpt(
        "warm",
        default=True,
        help="""
Pre-warm the modules (eg. load models, do preliminary checks, etc). You might
want to disable this option if DEEPaaS is loading more than one module because
you risk getting out of memory errors.
""",
    ),
    cfg.StrOpt(
        "model-name",
        default=os.environ.get("DEEPAAS_V2_MODEL", ""),
        help="""
Specify the model to be used. If not specified, DEEPaaS will serve all the models that
are available. If specified, DEEPaaS will serve only the specified model. You can also
use the DEEPAAS_V2_MODEL environment variable.

WARNING: Serving multiple models is deprecated and will be removed in the future,
         therefore it is strongly suggested that you specify the model you want to
         or that you ensure that only one model is available.
""",
    ),
]

CONF = cfg.CONF
CONF.register_cli_opts(opts)


def prepare_logging():
    log.register_options(cfg.CONF)
    log.set_defaults(default_log_levels=log.get_default_log_levels())


def parse_args(argv, default_config_files=None):
    cfg.CONF(
        argv[1:],
        project="deepaas",
        version=deepaas.extract_version(),
        default_config_files=default_config_files,
    )


def config_and_logging(argv, default_config_files=None):
    prepare_logging()
    parse_args(argv, default_config_files=default_config_files)
    log.setup(cfg.CONF, "deepaas")
