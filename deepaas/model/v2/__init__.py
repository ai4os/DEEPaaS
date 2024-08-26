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
from deepaas.model.v2 import test
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
        # We do not raise here, as we have not yet removed the deprecated loading of the
        # test module... but we should remove it as soon as the code below is deprecated
        LOG.warning("Error loading models: %s", e)
        warnings.warn(
            "Error loading models, using test model. This will be deprecated soon.",
            DeprecationWarning,
            stacklevel=2,
        )

    if MODELS:
        if len(MODELS) > 1:
            # Loading several models will be deprecated in the future
            warn_msg = "Loading several models is deprecated."
            warnings.warn(warn_msg, DeprecationWarning, stacklevel=2)
            LOG.warning(warn_msg)

        MODELS_LOADED = True
        return

    if not MODELS:
        # Raise deprecation warning
        warn_msg = (
            "Using the built-in test model is deprecated, if you are testing the "
            "API, please use the demo_app instead. "
            "Check https://github.com/deephdc/demo_app for more information.",
        )
        warnings.warn(warn_msg, DeprecationWarning, stacklevel=2)
        LOG.info("No models found in V2, loading test model")
        LOG.warning(warn_msg)
        MODELS["deepaas-test"] = wrapper.ModelWrapper(
            "deepaas-test", test.TestModel(), app
        )
    MODELS_LOADED = True
