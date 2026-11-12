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

"""Tests for the parsing of the arguments declared by the models."""

import fastapi
from fastapi.testclient import TestClient
from marshmallow import fields
from marshmallow import validate
import pytest
import starlette.datastructures

from deepaas.api.v2 import utils


def _get_client(args):
    parse_arguments, parameters = utils.get_arguments_parser(args)
    app = fastapi.FastAPI()

    @app.post("/", openapi_extra={"parameters": parameters})
    async def handler(kwargs: dict = fastapi.Depends(parse_arguments)):  # noqa(B008)
        ret = {}
        for k, v in kwargs.items():
            if isinstance(v, starlette.datastructures.UploadFile):
                v = {"filename": v.filename, "content": (await v.read()).decode()}
            ret[k] = v
        return ret

    return TestClient(app)


@pytest.fixture
def args():
    return {
        "an-int": fields.Int(load_default=0),
        "a_bool": fields.Bool(load_default=False),
        "a_str": fields.Str(required=True, metadata={"description": "A string"}),
        "a_range": fields.Int(load_default=50, validate=validate.Range(min=1, max=100)),
        "a_choice": fields.Str(load_default="a", validate=validate.OneOf(["a", "b"])),
        "a_list": fields.List(fields.Float(), load_default=[0.1]),
        "a_dict": fields.Dict(load_default={}),
        "password": fields.Str(load_default="x", metadata={"format": "password"}),
    }


@pytest.fixture
def client(args):
    return _get_client(args)


def test_defaults(client):
    r = client.post("/", params={"a_str": "foo"})
    assert r.status_code == 200
    assert r.json() == {
        "an-int": 0,
        "a_bool": False,
        "a_str": "foo",
        "a_range": 50,
        "a_choice": "a",
        "a_list": [0.1],
        "a_dict": {},
        "password": "x",
    }


def test_query(client):
    r = client.post(
        "/",
        params=[
            ("a_str", "foo"),
            ("an-int", "3"),
            ("a_bool", "true"),
            ("a_list", "1.5"),
            ("a_list", "2.5"),
            ("a_dict", '{"a": 1}'),
        ],
    )
    assert r.status_code == 200
    data = r.json()
    assert data["an-int"] == 3
    assert data["a_bool"] is True
    assert data["a_list"] == [1.5, 2.5]
    assert data["a_dict"] == {"a": 1}


def test_form(client):
    r = client.post(
        "/",
        data={"a_str": "foo", "an-int": "3", "a_list": ["1", "2"]},
    )
    assert r.status_code == 200
    assert r.json()["an-int"] == 3
    assert r.json()["a_list"] == [1.0, 2.0]


def test_json_body(client):
    r = client.post("/", json={"a_str": "foo", "an-int": 3, "a_list": [1, 2]})
    assert r.status_code == 200
    assert r.json()["an-int"] == 3
    assert r.json()["a_list"] == [1.0, 2.0]


def test_list_as_json_string(client):
    r = client.post("/", params={"a_str": "foo", "a_list": "[1, 2]"})
    assert r.status_code == 200
    assert r.json()["a_list"] == [1.0, 2.0]


def test_query_has_precedence(client):
    r = client.post("/", params={"a_str": "query"}, data={"a_str": "form"})
    assert r.json()["a_str"] == "query"


def test_unknown_arguments_are_ignored(client):
    r = client.post("/", params={"a_str": "foo", "unknown": "bar"})
    assert r.status_code == 200
    assert "unknown" not in r.json()


@pytest.mark.parametrize(
    "params,field",
    [
        ({}, "a_str"),
        ({"a_str": "foo", "an-int": "foo"}, "an-int"),
        ({"a_str": "foo", "a_range": "500"}, "a_range"),
        ({"a_str": "foo", "a_choice": "c"}, "a_choice"),
    ],
)
def test_validation_errors(client, params, field):
    r = client.post("/", params=params)
    assert r.status_code == 422
    errors = r.json()["detail"]
    assert [e["loc"] for e in errors] == [["query", field]]


def test_files():
    client = _get_client(
        {
            "data": fields.Raw(required=True, metadata={"type": "file"}),
            "other-file": fields.Raw(metadata={"type": "file"}),
            "param": fields.Int(load_default=1),
        }
    )
    r = client.post(
        "/",
        files={"data": ("a.txt", b"content")},
        data={"param": "2"},
    )
    assert r.status_code == 200
    assert r.json() == {
        "data": {"filename": "a.txt", "content": "content"},
        "other-file": None,
        "param": 2,
    }

    r = client.post(
        "/",
        files={"data": ("a.txt", b"a"), "other-file": ("b.txt", b"b")},
        params={"param": "3"},
    )
    assert r.status_code == 200
    assert r.json()["other-file"] == {"filename": "b.txt", "content": "b"}
    assert r.json()["param"] == 3

    r = client.post("/", data={"param": "2"})
    assert r.status_code == 422


def test_openapi(client):
    spec = client.get("/openapi.json").json()
    params = {p["name"]: p for p in spec["paths"]["/"]["post"]["parameters"]}
    assert set(params) == {
        "an-int",
        "a_bool",
        "a_str",
        "a_range",
        "a_choice",
        "a_list",
        "a_dict",
        "password",
    }
    assert all(p["in"] == "query" for p in params.values())
    assert params["a_str"]["required"] is True
    assert params["a_str"]["description"] == "A string"
    assert params["an-int"]["schema"] == {"type": "integer", "default": 0}
    assert params["a_bool"]["schema"]["default"] is False
    assert params["a_range"]["schema"]["minimum"] == 1
    assert params["a_range"]["schema"]["maximum"] == 100
    assert params["a_choice"]["schema"]["enum"] == ["a", "b"]
    assert params["a_list"]["schema"]["type"] == "array"
    assert params["password"]["schema"]["format"] == "password"


def test_openapi_file_names():
    client = _get_client(
        {
            "image": fields.Raw(required=True, metadata={"type": "file"}),
            "other-file": fields.Raw(metadata={"type": "file"}),
        }
    )
    spec = client.get("/openapi.json").json()
    body = spec["paths"]["/"]["post"]["requestBody"]["content"]
    ref = body["multipart/form-data"]["schema"]["$ref"].split("/")[-1]
    properties = spec["components"]["schemas"][ref]["properties"]
    # Files are documented with their names, so that clients send them right
    assert "image" in properties

    r = client.post("/", files={"image": ("a.txt", b"a")})
    assert r.status_code == 200
    assert r.json()["image"] == {"filename": "a.txt", "content": "a"}
