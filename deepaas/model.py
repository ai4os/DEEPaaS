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

from deepaas import loading

try:
    # FIXME(aloga): we are only using one
    # FIXME(aloga): use a singleton here
    MODEL = loading.get_available_models().items()[0]
except Exception as e:
    # TODO(aloga): use logging, not prints
    print("Cannot load model: %s" % e)
    MODEL = None
