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

deepaas_test_meta = {
    'author': 'Alvaro Lopez Garcia',
    'description': ('This is not a model at all, just a '
                    'placeholder for testing the API '
                    'functionality. If you are seeing this, it is '
                    'because DEEPaaS could not load a valid model.'),
    'id': '0',
    'links': [
        {
            'href': '/v2/models/deepaas-test',
            'rel': 'self'
        }
    ],
    'name': 'deepaas-test',
    'url': "https://github.com/indigo-dc/DEEPaaS/",
    'license': "Apache 2.0",
    'version': '0.0.1'
}

models_meta = {
    'models': [
        deepaas_test_meta,
    ]
}

v2_version = {
    'version': 'stable',
    'id': 'v2',
    'links': [
        {
            'href': '/v2/',
            'rel': 'self'
        }
    ],
}

v1_version = {
    'version': 'deprecated',
    'id': 'v1',
    'links': [
        {
            'href': '/v1/',
            'rel': 'self'
        }
    ],
}

all_versions = {
    'versions': [
        v1_version,
        v2_version,
    ]
}

versions = {
    'versions': [
        v2_version,
    ]
}

deepaas_test_predict = {
    'date': '2019-01-1',
    'labels': [
        {'label': 'foo', 'probability': 1.0}
    ]
}

deepaas_test_train = {
    'status': 'running',
    'uuid': '2ad53089edfb4521af081c45df16bed5'
}
