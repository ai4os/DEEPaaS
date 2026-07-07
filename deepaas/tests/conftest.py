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

"""Shared pytest fixtures for the DEEPaaS test suite.

The ``test_app`` and ``client`` fixtures create a real FastAPI application
backed by the ``fake_v2_model.TestModel`` dummy model.  They are
session-scoped so the (somewhat expensive) app-initialisation only happens
once per test run.
"""

from unittest import mock

import pytest
from fastapi.testclient import TestClient

import deepaas.api as api_module
import deepaas.api.v2 as v2_module
import deepaas.model as model_module
import deepaas.model.loading
import deepaas.model.v2 as model_v2
from deepaas.tests import fake_v2_model

#: The model name that ``fake_v2_model.TestModel`` advertises.
TEST_MODEL_NAME = "deepaas-test"


def _reset_api_singletons():
    """Reset every module-level singleton that ``get_fastapi_app`` touches.

    This must be called before the test application is created so that we
    always start from a clean slate, regardless of what other tests may have
    done earlier in the session.
    """
    api_module.APP = None
    api_module.VERSIONS = {}
    v2_module.APP = None
    model_v2.MODEL = None
    model_v2.MODEL_NAME = ""
    model_module.V2_MODEL = None
    model_module.V2_MODEL_NAME = None


@pytest.fixture(scope="session")
def test_app():
    """Return a configured FastAPI application for API-level tests.

    Model loading is mocked so the tests do not depend on any installed
    entry-point plugins.  Documentation endpoints are enabled so that the
    ``/docs``, ``/redoc``, and ``/openapi.json`` routes are available.
    """
    _reset_api_singletons()

    with mock.patch.object(
        deepaas.model.loading,
        "get_available_model_names",
        return_value=[TEST_MODEL_NAME],
    ), mock.patch.object(
        deepaas.model.loading,
        "get_model_by_name",
        return_value=fake_v2_model.TestModel,
    ):
        app = api_module.get_fastapi_app(enable_doc=True)

    return app


@pytest.fixture(scope="session")
def client(test_app):
    """Return a ``TestClient`` wrapping the test application."""
    with TestClient(test_app) as c:
        yield c
