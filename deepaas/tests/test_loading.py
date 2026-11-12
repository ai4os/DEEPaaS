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

"""Tests for the loading of the models through entry points."""

import importlib.metadata
import types

import pytest
import stevedore
import stevedore.extension

from deepaas import config
from deepaas import exceptions
import deepaas.model.v2
from deepaas.model import loading
from deepaas.model.v2 import wrapper as v2_wrapper
from deepaas.tests import fake_v2_model


def _module_model(name="module-model"):
    module = types.ModuleType(name)
    module.get_metadata = lambda: {"name": name}
    return module


@pytest.fixture
def entry_points(monkeypatch):
    """Fake the models installed in the system.

    The real stevedore managers are used, built from fake extensions, so
    that the code in deepaas.model.loading is exercised.
    """
    plugins = {}
    real_manager = stevedore.ExtensionManager
    real_named_manager = stevedore.NamedExtensionManager

    def _extensions(names=None):
        return [
            stevedore.extension.Extension(
                name,
                importlib.metadata.EntryPoint(
                    name, f"fake:{name}", loading.NAMESPACES["v2"]
                ),
                plugin,
                None,
            )
            for name, plugin in plugins.items()
            if names is None or name in names
        ]

    def extension_manager(namespace, **kwargs):
        assert namespace == loading.NAMESPACES["v2"]
        return real_manager.make_test_instance(_extensions(), namespace=namespace)

    def named_extension_manager(namespace, names, **kwargs):
        assert namespace == loading.NAMESPACES["v2"]
        return real_named_manager.make_test_instance(
            _extensions(names), namespace=namespace
        )

    monkeypatch.setattr(stevedore, "ExtensionManager", extension_manager)
    monkeypatch.setattr(stevedore, "NamedExtensionManager", named_extension_manager)
    monkeypatch.setattr(deepaas.model.v2, "MODEL", None)
    monkeypatch.setattr(deepaas.model.v2, "MODEL_NAME", "")
    return plugins


def test_get_available_model_names(entry_points):
    assert loading.get_available_model_names("v2") == frozenset()
    entry_points["foo"] = object()
    entry_points["bar"] = object()
    assert loading.get_available_model_names("v2") == {"foo", "bar"}


def test_get_available_models(entry_points):
    foo, bar = object(), object()
    entry_points.update(foo=foo, bar=bar)
    assert loading.get_available_models("v2") == {"foo": foo, "bar": bar}


def test_get_model_by_name(entry_points):
    foo = object()
    entry_points.update(foo=foo, bar=object())
    assert loading.get_model_by_name("foo", "v2") is foo


def test_get_model_by_name_not_found(entry_points):
    entry_points["foo"] = object()
    with pytest.raises(exceptions.ModuleNotFoundError):
        loading.get_model_by_name("bar", "v2")


def test_load_single_model(entry_points):
    module = _module_model()
    entry_points["module-model"] = module
    deepaas.model.v2.load_model()

    assert deepaas.model.v2.MODEL_NAME == "module-model"
    assert isinstance(deepaas.model.v2.MODEL, v2_wrapper.ModelWrapper)
    assert deepaas.model.v2.MODEL.model_obj is module


def test_load_class_model(entry_points):
    entry_points["class-model"] = fake_v2_model.TestModel
    deepaas.model.v2.load_model()

    assert isinstance(deepaas.model.v2.MODEL.model_obj, fake_v2_model.TestModel)


def test_load_no_models(entry_points):
    with pytest.raises(exceptions.NoModelsAvailable):
        deepaas.model.v2.load_model()


def test_load_multiple_models(entry_points):
    entry_points.update(foo=_module_model("foo"), bar=_module_model("bar"))
    with pytest.raises(exceptions.MultipleModelsFound):
        deepaas.model.v2.load_model()


def test_load_model_by_name(entry_points, monkeypatch):
    entry_points.update(foo=_module_model("foo"), bar=_module_model("bar"))
    monkeypatch.setattr(config.CONF, "model_name", "bar")
    deepaas.model.v2.load_model()

    assert deepaas.model.v2.MODEL_NAME == "bar"
    assert deepaas.model.v2.MODEL.get_metadata() == {"name": "bar"}


def test_load_model_by_name_not_found(entry_points, monkeypatch):
    entry_points["foo"] = _module_model("foo")
    monkeypatch.setattr(config.CONF, "model_name", "bar")
    with pytest.raises(exceptions.ModuleNotFoundError):
        deepaas.model.v2.load_model()
    assert deepaas.model.v2.MODEL is None


def test_load_model_failing_on_init(entry_points):
    class Model(object):
        def __init__(self):
            raise RuntimeError("cannot load weights")

    entry_points["foo"] = Model
    with pytest.raises(RuntimeError, match="cannot load weights"):
        deepaas.model.v2.load_model()
    assert deepaas.model.v2.MODEL is None
