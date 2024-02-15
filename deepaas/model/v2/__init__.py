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

from oslo_log import log

from deepaas.model import loading
from deepaas.model.v2 import test
from deepaas.model.v2 import wrapper

import warnings
import sys

LOG = log.getLogger(__name__)

# Model registry
MODELS = {}
MODELS_LOADED = False

# Adding the possibility of introducing the model you want to register in case you have tried to load several models. 
# If more than one model is introduced and the user doesn't select only one to load, an error is raised and all models are
# unloaded.
def register_models(app, selected_model=None):
    global MODELS
    global MODELS_LOADED

    if len(MODELS) > 1:
        warnings.warn(
            "Loading several models at once",
            DeprecationWarning
        )
        if selected_model is None:
            MODELS.clear()
            sys.stderr.write(
                "ERROR: Tried to load several models when only one is allowed to be loaded at a time.\n"
                "Please indicate which one you would like to load or load a single model. \n"
                "All models have been unloaded. \n"
            )
            sys.exit(1)
    
    if MODELS_LOADED:
        return

    try:
        for name, model in loading.get_available_models("v2").items():
            MODELS[name] = wrapper.ModelWrapper(name, model, app)
    except Exception as e:
        LOG.warning("Error loading models: %s", e)

    if len(MODELS) > 1:
        warnings.warn(
            "Loading several models at once",
            DeprecationWarning
        )

        if selected_model in MODELS.keys():
            loaded_model = MODELS[selected_model]
            MODELS.clear()
            MODELS[selected_model] =  loaded_model
        else:
            MODELS.clear()
            sys.stderr.write(
                "ERROR: Tried to load several models when only one is allowed to be loaded at a time.\n"
                "Please indicate which one you would like to load or load a single model. \n"
                "All models have been unloaded. \n"
            )
            sys.exit(1)

    if MODELS:
        MODELS_LOADED = True
        return

    if not MODELS:
        LOG.info("No models found in V2, loading test model")
        MODELS["deepaas-test"] = wrapper.ModelWrapper(
            "deepaas-test", test.TestModel(), app
        )
    MODELS_LOADED = True
