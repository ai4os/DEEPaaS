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

from deepaas.model import v2

V2_MODELS = v2.MODELS

# Backwards compatibility - these will be updated after model registration
V2_MODEL = None
V2_MODEL_NAME = None


def register_v2_models(app):
    """Register V2 models.

    This method has to be called before the API is spawned, so that we
    can look up the correct entry points and load the defined models.
    """
    global V2_MODEL, V2_MODEL_NAME
    
    result = v2.register_models(app)
    
    # Update backwards compatibility variables
    if V2_MODELS:
        model_names = list(V2_MODELS.keys())
        V2_MODEL_NAME = model_names[0]
        V2_MODEL = V2_MODELS[V2_MODEL_NAME]
    
    return result
