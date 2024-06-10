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

import warnings

from oslo_log import log

from deepaas import config
from deepaas import exceptions
from deepaas.model import loading
from deepaas.model.v2 import wrapper

LOG = log.getLogger(__name__)

CONF = config.CONF

# Model registry
MODELS = {}
MODELS_LOADED = False


def register_models(app):
    global MODELS
    global MODELS_LOADED

    if MODELS_LOADED:
        return

    try:
        if CONF.model_name:
            MODELS[CONF.model_name] = wrapper.ModelWrapper(
                CONF.model_name,
                loading.get_model_by_name(CONF.model_name, "v2"),
                app,
            )
        else:
            for name, model in loading.get_available_models("v2").items():
                MODELS[name] = wrapper.ModelWrapper(name, model, app)
    except exceptions.ModuleNotFoundError:
        LOG.error("Model not found: %s", CONF.model_name)
        raise
    except Exception as e:
        LOG.warning("Error loading models: %s", e)
        raise e

    if MODELS:
        if len(MODELS) > 1:
            # Loading several models will be deprecated in the future
            warn_msg = "Loading several models is deprecated."
            warnings.warn(warn_msg, DeprecationWarning, stacklevel=2)
            LOG.warning(warn_msg)

        MODELS_LOADED = True
        return

    if not MODELS:
        LOG.error("No models found in V2, loading test model")
        raise exceptions.NoModelsAvailable()
    MODELS_LOADED = True
