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

from deepaas.model import v1
from deepaas.model import v2

V1_MODELS = v1.MODELS
V2_MODELS = v2.MODELS


def register_v1_models():
    """Register V1 models.

    This method has to be called before the API is spawned, so that we
    can look up the correct entry points and load the defined models.
    """

    return v1.register_models()


def register_v2_models(app):
    """Register V2 models.

    This method has to be called before the API is spawned, so that we
    can look up the correct entry points and load the defined models.
    """

    return v2.register_models(app)
