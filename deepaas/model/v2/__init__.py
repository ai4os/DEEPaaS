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

from deepaas import config
from deepaas import exceptions
from deepaas import log
from deepaas.model import loading
from deepaas.model.v2 import wrapper

LOG = log.getLogger(__name__)

CONF = config.CONF

# Model registry - simplified for single model use case
MODEL = None
MODEL_NAME = ""


def register_models(app):
    """Register a single V2 model.
    
    Since DEEPaaS only handles one model at a time, this is simplified
    to manage a single model instance.
    """
    global MODEL
    global MODEL_NAME

    if MODEL:
        return

    if CONF.model_name:
        model_name = CONF.model_name
    else:
        model_names = list(loading.get_available_model_names("v2"))
        if not model_names:
            LOG.error("No models found.")
            raise exceptions.NoModelsAvailable()
        elif len(model_names) == 1:
            model_name = model_names[0]
        else:
            LOG.error(
                "Multiple models found, but no model has been specified, please "
                "specify a model using the --model-name option."
            )
            raise exceptions.MultipleModelsFound()

    try:
        MODEL = wrapper.ModelWrapper(
            model_name,
            loading.get_model_by_name(model_name, "v2"),
        )
        MODEL_NAME = model_name
    except exceptions.ModuleNotFoundError:
        LOG.error("Model not found: %s", model_name)
        raise
    except Exception as e:
        LOG.exception("Error loading model: %s", e)
        raise e
