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

# Direct access to the single model
V2_MODEL = None
V2_MODEL_NAME = None


def register_v2_models(app):
    """Register V2 models.

    This method has to be called before the API is spawned, so that we
    can look up the correct entry points and load the defined models.
    """
    global V2_MODEL, V2_MODEL_NAME
    
    v2.register_models(app)
    
    # Update module-level variables for easy access
    V2_MODEL = v2.MODEL
    V2_MODEL_NAME = v2.MODEL_NAME


# For compatibility with code that expects V2_MODELS dictionary
def __getattr__(name):
    if name == 'V2_MODELS':
        # Return a dict-like interface for the single model
        if V2_MODEL and V2_MODEL_NAME:
            return {V2_MODEL_NAME: V2_MODEL}
        return {}
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
