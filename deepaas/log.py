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

logging.captureWarnings(True)

LOG = logging.getLogger("deepaas")


log_format = (
    "%(asctime)s.%(msecs)03d %(process)d %(levelname)s %(name)s [-] %(message)s"
)
log_format_debug_suffix = "%(funcName)s %(pathname)s:%(lineno)d"


def getLogger(name):  # noqa
    return LOG.getChild(name)


def setup(log_level, log_file=None):
    LOG.setLevel(log_level)

    if log_level == "DEBUG":
        format_ = log_format + " [-] " + log_format_debug_suffix
    else:
        format_ = log_format

    logging.basicConfig(level=log_level, format=format_)

    if log_file:
        fh = logging.FileHandler(log_file)
        fh.setLevel(log_level)
        LOG.addHandler(fh)
    else:
        ch = logging.StreamHandler()
        ch.setLevel(log_level)
        LOG.addHandler(ch)
