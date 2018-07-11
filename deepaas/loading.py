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

import stevedore

MODEL_NAMESPACE = "deepaas.model"


def get_available_model_names():
    """Get the names of all the models that are available on the system.

    :returns: A list of names.
    :rtype: frozenset
    """
    mgr = stevedore.ExtensionManager(namespace=MODEL_NAMESPACE)
    return frozenset(mgr.names())


def get_available_models():
    """Retrieve all the models available on the system.

    :returns: A dict with model entrypoint name as the key and the model
              as the value.
    :rtype: dict
    """
    mgr = stevedore.ExtensionManager(namespace=MODEL_NAMESPACE,
                                     propagate_map_exceptions=True)

    return dict(mgr.map(lambda ext: (ext.entry_point.name, ext.plugin)))
