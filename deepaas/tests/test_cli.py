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

"""Tests for the deepaas-cli command."""

import json
import types

import pytest

from deepaas.cmd import cli
from deepaas.model import loading
from deepaas.tests import fake_v2_model


@pytest.fixture
def models(monkeypatch):
    models = {"deepaas-test": fake_v2_model.TestModel}
    monkeypatch.setattr(loading, "get_available_models", lambda v: dict(models))
    return models


@pytest.fixture
def data_file(tmp_path):
    path = tmp_path / "data.txt"
    path.write_text("some data")
    return str(path)


def test_help(models, capsys):
    with pytest.raises(SystemExit) as e:
        cli.main(["--help"])
    assert e.value.code == 0
    out = capsys.readouterr().out
    assert "{get_metadata,warm,predict}" in out
    assert "--model-name" in out


def test_predict_help(models, capsys):
    with pytest.raises(SystemExit):
        cli.main(["predict", "--help"])
    out = capsys.readouterr().out
    assert "--data" in out
    assert "--parameter" in out
    assert "*Required*" in out


def test_get_metadata(models, capsys):
    cli.main(["get_metadata"])
    meta = json.loads(capsys.readouterr().out)
    assert meta["name"] == "deepaas-test"


def test_no_method_returns_metadata(models, capsys):
    cli.main([])
    meta = json.loads(capsys.readouterr().out)
    assert meta["name"] == "deepaas-test"


def test_get_metadata_output_file(models, tmp_path):
    out = tmp_path / "out" / "meta.json"
    cli.main(["--deepaas_method_output", str(out), "get_metadata"])
    assert json.loads(out.read_text())["name"] == "deepaas-test"


def test_warm(models):
    cli.main(["warm"])


def test_predict(models, data_file, capsys, monkeypatch):
    received = {}
    original = fake_v2_model.TestModel.predict

    def predict(self, **kwargs):
        received.update(kwargs)
        with open(kwargs["data"].filename) as f:
            received["content"] = f.read()
        return original(self, **kwargs)

    monkeypatch.setattr(fake_v2_model.TestModel, "predict", predict)
    cli.main(["predict", "--data", data_file, "--parameter", "3"])

    out = json.loads(capsys.readouterr().out)
    assert out["labels"][0]["label"] == "foo"
    assert received["parameter"] == 3
    assert received["content"] == "some data"
    f = received["data"]
    assert f.name == "data"
    assert f.original_filename == data_file
    assert f.content_type == "text/plain"


def test_predict_missing_required(models, data_file, capsys):
    with pytest.raises(SystemExit) as e:
        cli.main(["predict", "--data", data_file])
    assert e.value.code == 2
    assert "--parameter" in capsys.readouterr().err


def test_predict_output_file(models, data_file, tmp_path):
    out = tmp_path / "result"
    cli.main(
        [
            "--deepaas_method_output",
            str(out),
            "predict",
            "--data",
            data_file,
            "--parameter",
            "1",
        ]
    )
    # The extension is added if missing
    assert json.loads((tmp_path / "result.json").read_text())["labels"]


def test_model_name(models, capsys):
    models["other"] = types.SimpleNamespace(
        get_metadata=lambda: {"name": "other"}, get_predict_args=lambda: {}
    )
    cli.main(["--model-name", "other", "get_metadata"])
    assert json.loads(capsys.readouterr().out) == {"name": "other"}


def test_model_name_from_environment(models, capsys, monkeypatch):
    models["other"] = types.SimpleNamespace(get_metadata=lambda: {"name": "other"})
    monkeypatch.setenv("DEEPAAS_V2_MODEL", "other")
    cli.main(["get_metadata"])
    assert json.loads(capsys.readouterr().out) == {"name": "other"}


def test_unknown_model(models, capsys):
    with pytest.raises(SystemExit) as e:
        cli.main(["--model-name", "foo", "get_metadata"])
    assert e.value.code == 1
    assert "deepaas-test" in capsys.readouterr().err


def test_several_models(models, capsys):
    models["other"] = object()
    with pytest.raises(SystemExit) as e:
        cli.main(["get_metadata"])
    assert e.value.code == 1
    assert "--model-name" in capsys.readouterr().err


def test_class_models_are_instantiated(models, capsys):
    cli.main(["get_metadata"])
    # TestModel.get_metadata is an instance method, it fails on the class
    assert json.loads(capsys.readouterr().out)["name"] == "deepaas-test"


def test_module_models_are_not_instantiated(models, capsys):
    models.clear()
    models["module"] = types.ModuleType("module")
    models["module"].get_metadata = lambda: {"name": "module"}
    models["module"].get_predict_args = lambda: {}
    cli.main(["get_metadata"])
    assert json.loads(capsys.readouterr().out) == {"name": "module"}


def _no_args():
    raise NotImplementedError()


@pytest.mark.parametrize(
    "model",
    [
        types.SimpleNamespace(get_metadata=lambda: {"name": "other"}),
        types.SimpleNamespace(
            get_metadata=lambda: {"name": "other"}, get_predict_args=_no_args
        ),
    ],
)
def test_model_without_predict_args(models, capsys, model):
    models.clear()
    models["other"] = model
    cli.main(["get_metadata"])
    assert json.loads(capsys.readouterr().out) == {"name": "other"}
