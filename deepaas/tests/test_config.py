# -*- coding: utf-8 -*-

# Copyright 2025 Spanish National Research Council (CSIC)
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

"""Tests for the DEEPaaS configuration."""

import os

import pytest

from deepaas import config
from deepaas import opts as deepaas_opts

CONF = config.CONF

# NOTE: the conftest replaces it to ignore the configuration of the machine
_DEFAULT_CONFIG_DIRS = config._get_default_config_dirs


def _parse(*args, files=None):
    return config.parse_args(["deepaas-run", *args], default_config_files=files)


def _write(path, content):
    path.write_text(content)
    return str(path)


def test_defaults():
    _parse()
    assert CONF.model_name == ""
    assert CONF.warm is True
    assert CONF.debug is False
    assert CONF.log_level == "INFO"
    assert CONF.listen_port == 5000


def test_command_line():
    _parse("--model-name", "foo", "--log-level", "DEBUG", "--listen-port", "80")
    assert CONF.model_name == "foo"
    assert CONF.log_level == "DEBUG"
    assert CONF.listen_port == 80


@pytest.mark.parametrize(
    "args,expected",
    [
        ([], True),
        (["--warm"], True),
        (["--nowarm"], False),
    ],
)
def test_bool_flags(args, expected):
    _parse(*args)
    assert CONF.warm is expected


def test_short_flags():
    _parse("-d", "-p", "3")
    assert CONF.debug is True
    assert CONF.workers == 3


def test_bool_flags_are_exclusive(capsys):
    with pytest.raises(SystemExit):
        _parse("--warm", "--nowarm")


@pytest.mark.parametrize(
    "args",
    [
        ["--log-level", "FOO"],
        ["--listen-port", "foo"],
        ["--listen-port", "65536"],
        ["--client-max-size", "-1"],
        ["--workers", "0"],
        ["--unknown-option"],
    ],
)
def test_invalid_command_line(args, capsys):
    with pytest.raises(SystemExit) as e:
        _parse(*args)
    assert e.value.code == 2


def test_environment(monkeypatch):
    monkeypatch.setenv("DEEPAAS_MODEL_NAME", "foo")
    monkeypatch.setenv("DEEPAAS_WARM", "false")
    monkeypatch.setenv("DEEPAAS_LISTEN_PORT", "8080")
    _parse()
    assert CONF.model_name == "foo"
    assert CONF.warm is False
    assert CONF.listen_port == 8080


def test_legacy_model_environment(monkeypatch):
    monkeypatch.setenv("DEEPAAS_V2_MODEL", "foo")
    _parse()
    assert CONF.model_name == "foo"


def test_new_model_environment_has_precedence(monkeypatch):
    monkeypatch.setenv("DEEPAAS_V2_MODEL", "foo")
    monkeypatch.setenv("DEEPAAS_MODEL_NAME", "bar")
    _parse()
    assert CONF.model_name == "bar"


def test_legacy_oslo_environment(monkeypatch):
    monkeypatch.setenv("OS_DEFAULT__AUTH_BEARER_TOKEN", "secret")
    with pytest.warns(DeprecationWarning, match="DEEPAAS_AUTH_BEARER_TOKEN"):
        _parse()
    assert CONF.auth_bearer_token == "secret"  # nosec


def test_invalid_environment(monkeypatch, capsys):
    monkeypatch.setenv("DEEPAAS_LISTEN_PORT", "foo")
    with pytest.raises(SystemExit):
        _parse()
    assert "DEEPAAS_LISTEN_PORT" in capsys.readouterr().err


def test_config_file(tmp_path):
    conf = _write(
        tmp_path / "deepaas.conf",
        "[DEFAULT]\n"
        "model_name = foo\n"
        "warm = False\n"
        "log-level = WARNING\n"
        "unknown_option = ignored\n",
    )
    _parse("--config-file", conf)
    assert CONF.model_name == "foo"
    assert CONF.warm is False
    assert CONF.log_level == "WARNING"


def test_config_files_precedence(tmp_path):
    one = _write(tmp_path / "one.conf", "[DEFAULT]\nmodel_name = one\nwarm = no\n")
    two = _write(tmp_path / "two.conf", "[DEFAULT]\nmodel_name = two\n")
    _parse("--config-file", one, "--config-file", two)
    assert CONF.model_name == "two"
    assert CONF.warm is False


def test_config_dir(tmp_path):
    conf_d = tmp_path / "deepaas.conf.d"
    conf_d.mkdir()
    _write(conf_d / "01.conf", "[DEFAULT]\nmodel_name = one\nwarm = no\n")
    _write(conf_d / "02.conf", "[DEFAULT]\nmodel_name = two\n")
    _write(conf_d / "ignored.txt", "[DEFAULT]\nmodel_name = ignored\n")
    _parse("--config-dir", str(conf_d))
    assert CONF.model_name == "two"
    assert CONF.warm is False


def test_default_config_files(tmp_path):
    conf = _write(tmp_path / "deepaas.conf", "[DEFAULT]\nmodel_name = foo\n")
    _parse(files=[conf])
    assert CONF.model_name == "foo"


def test_precedence(tmp_path, monkeypatch):
    conf = _write(
        tmp_path / "deepaas.conf",
        "[DEFAULT]\nmodel_name = file\nlog_level = ERROR\nlisten_port = 1\n",
    )
    monkeypatch.setenv("DEEPAAS_MODEL_NAME", "env")
    monkeypatch.setenv("DEEPAAS_LOG_LEVEL", "WARNING")
    _parse("--config-file", conf, "--model-name", "cli")
    assert CONF.model_name == "cli"
    assert CONF.log_level == "WARNING"
    assert CONF.listen_port == 1


def test_missing_config_file(tmp_path, capsys):
    with pytest.raises(SystemExit):
        _parse("--config-file", str(tmp_path / "missing.conf"))
    assert "missing.conf" in capsys.readouterr().err


@pytest.mark.parametrize(
    "content",
    [
        "[DEFAULT]\nwarm = maybe\n",
        "[DEFAULT]\nlog_level = FOO\n",
        "not an ini file",
    ],
)
def test_invalid_config_file(tmp_path, content, capsys):
    conf = _write(tmp_path / "deepaas.conf", content)
    with pytest.raises(SystemExit):
        _parse("--config-file", conf)
    assert "deepaas.conf" in capsys.readouterr().err


def test_deprecated_option():
    with pytest.warns(DeprecationWarning, match="client_max_size"):
        _parse("--client-max-size", "2")


def test_find_config_files(tmp_path, monkeypatch):
    home = tmp_path / "home"
    etc = tmp_path / "etc"
    (home / ".deepaas").mkdir(parents=True)
    (etc / "deepaas" / "deepaas.conf.d").mkdir(parents=True)
    _write(home / ".deepaas" / "deepaas.conf", "")
    _write(etc / "deepaas" / "deepaas.conf", "")
    _write(etc / "deepaas" / "deepaas-run.conf", "")
    _write(etc / "deepaas" / "deepaas.conf.d" / "b.conf", "")
    _write(etc / "deepaas" / "deepaas.conf.d" / "a.conf", "")

    monkeypatch.setattr(
        config,
        "_get_default_config_dirs",
        lambda project: [str(home / ".deepaas"), str(home), str(etc / "deepaas")],
    )
    d = etc / "deepaas"
    assert config.find_config_files(prog="deepaas-run") == [
        # The first deepaas.conf found, then the first deepaas-run.conf
        str(home / ".deepaas" / "deepaas.conf"),
        str(d / "deepaas-run.conf"),
        # Then the deepaas.conf.d directories, in alphabetical order
        str(d / "deepaas.conf.d" / "a.conf"),
        str(d / "deepaas.conf.d" / "b.conf"),
    ]

    # The default files are used if none is given in the command line
    _write(d / "deepaas-run.conf", "[DEFAULT]\nmodel_name = foo\n")
    config.parse_args(["deepaas-run"])
    assert CONF.model_name == "foo"


def test_default_config_dirs():
    dirs = _DEFAULT_CONFIG_DIRS("deepaas")
    assert dirs[:2] == [os.path.expanduser("~/.deepaas"), os.path.expanduser("~")]
    assert dirs[-2:] == ["/etc/deepaas", "/etc"]


def test_sample():
    sample = deepaas_opts.generate_sample()
    assert sample.startswith("[DEFAULT]")
    for _, group in deepaas_opts.list_opts():
        for opt in group:
            assert f"#{opt.dest} = " in sample
            assert f"# Environment variable: {opt.env_vars[0]}" in sample
