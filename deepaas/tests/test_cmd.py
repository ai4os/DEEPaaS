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

import pathlib
import sys
from unittest import mock

from oslo_config import cfg
import pytest

from deepaas.cmd import run
import deepaas.config

CONF = cfg.CONF


@pytest.fixture
def fastapi_app_fixture():
    return mock.MagicMock()


@pytest.fixture
def uvicorn_run_fixture():
    return mock.MagicMock()


def test_run(monkeypatch, fastapi_app_fixture, uvicorn_run_fixture):
    """Test the run command."""
    monkeypatch.setattr(deepaas.cmd._shutdown, "handle_signals", mock.MagicMock())
    monkeypatch.setattr(deepaas.api, "get_fastapi_app", fastapi_app_fixture)
    monkeypatch.setattr("uvicorn.run", uvicorn_run_fixture)

    # Monkeypatch the argv, as otherwise it will get the testing cmd line
    monkeypatch.setattr(sys, "argv", ["deepaas-run"])
    run.main()

    fastapi_app_fixture.assert_called_once()
    uvicorn_run_fixture.assert_called_with(
        fastapi_app_fixture(),
        host="127.0.0.1",
        port=5000,
    )


@pytest.fixture
def cfg_fixture():
    # Keep track of which flags were overridden
    overridden_flags = []

    def set_flag(flag, value):
        CONF.set_override(flag, value)
        overridden_flags.append(flag)

    yield set_flag

    # Clean up after the test
    for flag in overridden_flags:
        CONF.clear_override(flag)


def test_run_custom_ip_port(
    monkeypatch, cfg_fixture, fastapi_app_fixture, uvicorn_run_fixture
):
    """Run the cmd line with a custom IP and port."""
    monkeypatch.setattr(deepaas.config, "setup", lambda x: None)

    ip = "1.1.1.1"
    port = 1234
    cfg_fixture("listen_ip", ip)
    cfg_fixture("listen_port", port)

    monkeypatch.setattr(deepaas.api, "get_fastapi_app", fastapi_app_fixture)
    monkeypatch.setattr("uvicorn.run", uvicorn_run_fixture)

    monkeypatch.setattr(sys, "argv", ["deepaas-run"])
    run.main()

    fastapi_app_fixture.assert_called_once()
    uvicorn_run_fixture.assert_called_with(fastapi_app_fixture(), host=ip, port=port)


def test_custom_base_path(monkeypatch, cfg_fixture, fastapi_app_fixture):
    """Run the cmd line with a custom base path."""
    monkeypatch.setattr(deepaas.config, "setup", lambda x: None)

    base_path = "/foo/bar"
    cfg_fixture("base_path", base_path)

    monkeypatch.setattr(deepaas.api, "get_fastapi_app", fastapi_app_fixture)
    monkeypatch.setattr("uvicorn.run", mock.MagicMock())

    monkeypatch.setattr(sys, "argv", ["deepaas-run"])
    run.main()

    fastapi_app_fixture.assert_called_once()
    fastapi_app_fixture.assert_called_with(
        enable_doc=True, base_path=str(pathlib.Path(base_path))
    )


def test_custom_base_path_no_slash(monkeypatch, cfg_fixture, fastapi_app_fixture):
    """Run the cmd line with a custom base path without a slash."""
    monkeypatch.setattr(deepaas.config, "setup", lambda x: None)

    base_path = "foo/bar"
    cfg_fixture("base_path", base_path)

    monkeypatch.setattr(deepaas.api, "get_fastapi_app", fastapi_app_fixture)
    monkeypatch.setattr("uvicorn.run", mock.MagicMock())

    monkeypatch.setattr(sys, "argv", ["deepaas-run"])
    mock_exit = mock.MagicMock()
    monkeypatch.setattr(sys, "exit", mock_exit)
    run.main()

    mock_exit.assert_called_once_with(1)
    fastapi_app_fixture.assert_called_once()
    fastapi_app_fixture.assert_called_with(
        enable_doc=True, base_path=str(pathlib.Path(base_path))
    )


def test_doc_endpoint_disabled(monkeypatch, cfg_fixture, fastapi_app_fixture):
    """Run the cmd line with doc endpoint disabled."""
    monkeypatch.setattr(deepaas.config, "setup", lambda x: None)

    cfg_fixture("doc_endpoint", False)

    monkeypatch.setattr(deepaas.api, "get_fastapi_app", fastapi_app_fixture)
    monkeypatch.setattr("uvicorn.run", mock.MagicMock())

    monkeypatch.setattr(sys, "argv", ["deepaas-run"])
    run.main()

    fastapi_app_fixture.assert_called_once()
    fastapi_app_fixture.assert_called_with(
        enable_doc=False, base_path=""
    )
