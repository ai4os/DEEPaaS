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

import pytest

from deepaas.cmd import run
import deepaas.config


@pytest.fixture
def fastapi_app_fixture(monkeypatch):
    m = mock.MagicMock()
    monkeypatch.setattr(deepaas.api, "get_fastapi_app", m)
    return m


@pytest.fixture
def uvicorn_run_fixture(monkeypatch):
    m = mock.MagicMock()
    monkeypatch.setattr("uvicorn.run", m)
    return m


@pytest.fixture
def run_main(monkeypatch, fastapi_app_fixture, uvicorn_run_fixture):
    """Run deepaas-run with the given command line arguments."""
    monkeypatch.setattr(deepaas.cmd._shutdown, "handle_signals", mock.MagicMock())
    monkeypatch.setattr(deepaas.log, "setup", mock.MagicMock())

    def _run(*args):
        monkeypatch.setattr(sys, "argv", ["deepaas-run", *args])
        run.main()

    return _run


def test_run(run_main, fastapi_app_fixture, uvicorn_run_fixture):
    """Test the run command."""
    run_main()

    fastapi_app_fixture.assert_called_once_with(enable_doc=True, base_path="")
    uvicorn_run_fixture.assert_called_with(
        fastapi_app_fixture(),
        host="127.0.0.1",
        port=5000,
    )


def test_run_custom_ip_port(run_main, fastapi_app_fixture, uvicorn_run_fixture):
    """Run the cmd line with a custom IP and port."""
    run_main("--listen-ip", "1.1.1.1", "--listen-port", "1234")

    fastapi_app_fixture.assert_called_once()
    uvicorn_run_fixture.assert_called_with(
        fastapi_app_fixture(), host="1.1.1.1", port=1234
    )


def test_run_ip_port_from_environment(
    run_main, monkeypatch, fastapi_app_fixture, uvicorn_run_fixture
):
    monkeypatch.setenv("DEEPAAS_LISTEN_IP", "0.0.0.0")  # nosec
    monkeypatch.setenv("DEEPAAS_LISTEN_PORT", "8080")
    run_main()

    uvicorn_run_fixture.assert_called_with(
        fastapi_app_fixture(), host="0.0.0.0", port=8080  # nosec
    )


def test_run_ip_port_from_config_file(
    run_main, tmp_path, fastapi_app_fixture, uvicorn_run_fixture
):
    conf = tmp_path / "deepaas.conf"
    conf.write_text("[DEFAULT]\nlisten_ip = 0.0.0.0\nlisten_port = 8080\n")
    run_main("--config-file", str(conf))

    uvicorn_run_fixture.assert_called_with(
        fastapi_app_fixture(), host="0.0.0.0", port=8080  # nosec
    )


@pytest.mark.parametrize("port", ["foo", "-1", "70000"])
def test_run_invalid_port(run_main, port, capsys):
    with pytest.raises(SystemExit) as e:
        run_main("--listen-port", port)
    assert e.value.code == 2
    assert "--listen-port" in capsys.readouterr().err


def test_custom_base_path(run_main, fastapi_app_fixture):
    """Run the cmd line with a custom base path."""
    base_path = "/foo/bar"
    run_main("--base-path", base_path)

    fastapi_app_fixture.assert_called_once_with(
        enable_doc=True, base_path=str(pathlib.Path(base_path))
    )


def test_custom_base_path_no_slash(run_main, fastapi_app_fixture):
    """Run the cmd line with a custom base path without a slash."""
    with pytest.raises(SystemExit) as e:
        run_main("--base-path", "foo/bar")

    assert e.value.code == 1
    fastapi_app_fixture.assert_not_called()


def test_doc_endpoint_disabled(run_main, fastapi_app_fixture):
    """Run the cmd line with doc endpoint disabled."""
    run_main("--nodoc-endpoint")

    fastapi_app_fixture.assert_called_once_with(enable_doc=False, base_path="")


def test_logging_setup(run_main):
    run_main("--debug", "--log-file", "/tmp/foo.log")  # nosec
    deepaas.log.setup.assert_called_once_with("DEBUG", "/tmp/foo.log")  # nosec
