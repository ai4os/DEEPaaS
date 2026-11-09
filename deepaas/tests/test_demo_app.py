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

"""Integration tests using the AI4OS demo application as the served model.

The demo application (https://github.com/ai4os-hub/ai4os-demo-app) is the
reference model for DEEPaaS, exercising all the argument types, file inputs
and the different response types. These tests load it through its real entry
point, without mocks, so they are skipped unless it is installed (e.g. run them
with ``tox -e demo-app``).
"""

import base64
import io
import json
import zipfile

from fastapi.testclient import TestClient
import pytest

pytest.importorskip(
    "ai4os_demo_app.api",
    reason="ai4os-demo-app is not installed, run 'tox -e demo-app'",
)

from deepaas import api as api_module  # noqa: E402
import deepaas.api.v2  # noqa: E402
from deepaas.cmd import cli  # noqa: E402
from deepaas import config  # noqa: E402
from deepaas import model  # noqa: E402
import deepaas.model.v2  # noqa: E402

MODEL_NAME = "ai4os_demo_app"
URL = f"/v2/models/{MODEL_NAME}/predict/"

IMAGE = b"\x89PNG\r\n\x1a\nfake image"
AUDIO = b"RIFF fake audio"
VIDEO = b"fake video"

_SINGLETONS = [
    (api_module, "APP"),
    (api_module, "VERSIONS"),
    (deepaas.api.v2, "APP"),
    (deepaas.model.v2, "MODEL"),
    (deepaas.model.v2, "MODEL_NAME"),
    (model, "V2_MODEL"),
    (model, "V2_MODEL_NAME"),
]


@pytest.fixture(scope="module")
def client():
    """Serve the demo application, loading it through its entry point."""
    saved = [(mod, attr, getattr(mod, attr)) for mod, attr in _SINGLETONS]
    api_module.APP = None
    api_module.VERSIONS = {}
    deepaas.model.v2.MODEL = None

    config.CONF.model_name = MODEL_NAME
    try:
        app = api_module.get_fastapi_app()
    finally:
        config.CONF.reset()

    with TestClient(app) as c:
        yield c

    for mod, attr, value in saved:
        setattr(mod, attr, value)


@pytest.fixture
def files():
    return {
        "demo_image": ("image.png", io.BytesIO(IMAGE), "image/png"),
        "demo_audio": ("audio.wav", io.BytesIO(AUDIO), "audio/wav"),
        "demo_video": ("video.mp4", io.BytesIO(VIDEO), "video/mp4"),
    }


def _b64(data):
    return base64.b64encode(data).decode("utf-8")


class TestMetadata:
    def test_model_is_listed(self, client):
        r = client.get("/v2/models/")
        assert r.status_code == 200
        models = r.json()["models"]
        assert [m["id"] for m in models] == [MODEL_NAME]

    def test_metadata(self, client):
        r = client.get(f"/v2/models/{MODEL_NAME}/")
        assert r.status_code == 200
        meta = r.json()
        assert meta["name"] == "ai4os_demo_app"
        assert meta["description"]
        assert meta["links"][0]["rel"] == "self"


class TestPredict:
    def test_defaults(self, client, files):
        r = client.post(URL, files=files)
        assert r.status_code == 200, r.text
        assert r.headers["content-type"] == "application/json"

        data = r.json()
        # The demo returns its inputs, checking that they have the right type
        # (e.g. that files are passed as UploadedFile objects)
        assert data["demo_str"] == "some-string"
        assert data["demo_int"] == 1
        assert data["demo_float"] == 0.1
        assert data["demo_bool"] is True
        assert data["demo_dict"] == {"a": 0, "b": 1}
        assert data["demo_list_of_floats"] == [0.1, 0.2, 0.3]
        assert data["demo_image"] == _b64(IMAGE)
        assert data["demo_audio"] == _b64(AUDIO)
        assert data["demo_video"] == _b64(VIDEO)
        assert len(data["labels"]) == len(data["probabilities"]) == 5

    @pytest.mark.parametrize("location", ["params", "data"])
    def test_arguments(self, client, files, location):
        # Arguments can be sent in the query string or as form fields
        args = {
            "demo_str": "foo",
            "demo_str_choice": "choice1",
            "demo_int": "0",
            "demo_int_range": "100",
            "demo_float": "0.5",
            "demo_bool": "false",
            "demo_dict": "{'c': 2}",
            "demo_list_of_floats": ["1.5", "2.5"],
        }
        r = client.post(URL, files=files, **{location: args})
        assert r.status_code == 200, r.text

        data = r.json()
        assert data["demo_str"] == "foo"
        assert data["demo_str_choice"] == "choice1"
        assert data["demo_int"] == 0
        assert data["demo_int_range"] == 100
        assert data["demo_float"] == 0.5
        assert data["demo_bool"] is False
        assert data["demo_dict"] == {"c": 2}
        assert data["demo_list_of_floats"] == [1.5, 2.5]

    def test_return_zip(self, client, files):
        r = client.post(URL, files=files, headers={"Accept": "application/zip"})
        assert r.status_code == 200, r.text
        assert r.headers["content-type"] == "application/zip"

        with zipfile.ZipFile(io.BytesIO(r.content)) as z:
            names = set(z.namelist())
            assert names == {
                "args.json",
                "demo_image.png",
                "demo_audio.wav",
                "demo_video.mp4",
            }
            assert z.read("demo_image.png") == IMAGE
            assert json.loads(z.read("args.json"))["demo_int"] == 1

    def test_return_image(self, client, files):
        r = client.post(URL, files=files, headers={"Accept": "image/*"})
        assert r.status_code == 200, r.text
        assert r.headers["content-type"] == "image/png"
        assert r.content == IMAGE

    def test_accept_any(self, client, files):
        r = client.post(URL, files=files, headers={"Accept": "*/*"})
        assert r.status_code == 200, r.text
        assert r.headers["content-type"] == "application/json"

    def test_accept_not_supported(self, client, files):
        r = client.post(URL, files=files, headers={"Accept": "text/html"})
        assert r.status_code == 406

    @pytest.mark.parametrize(
        "params,field",
        [
            ({"demo_int_range": "0"}, "demo_int_range"),
            ({"demo_int": "foo"}, "demo_int"),
            ({"demo_bool": "maybe"}, "demo_bool"),
            ({"demo_list_of_floats": "foo"}, "demo_list_of_floats"),
        ],
    )
    def test_invalid_arguments(self, client, files, params, field):
        r = client.post(URL, files=files, params=params)
        assert r.status_code == 422
        assert [e["loc"][-1] for e in r.json()["detail"]] == [field]

    def test_missing_files(self, client, files):
        del files["demo_audio"]
        del files["demo_video"]
        r = client.post(URL, files=files)
        assert r.status_code == 422
        missing = {e["loc"][-1] for e in r.json()["detail"]}
        assert missing == {"demo_audio", "demo_video"}


class TestOpenAPI:
    @pytest.fixture(scope="class")
    def operation(self, client):
        return client.get("/openapi.json").json()["paths"][URL]["post"]

    def test_parameters(self, operation):
        params = {p["name"]: p for p in operation["parameters"]}
        assert set(params) == {
            "demo_str",
            "demo_str_choice",
            "demo_password",
            "demo_int",
            "demo_int_range",
            "demo_float",
            "demo_bool",
            "demo_dict",
            "demo_list_of_floats",
        }
        assert all(p["in"] == "query" for p in params.values())
        assert params["demo_int_range"]["schema"]["minimum"] == 1
        assert params["demo_int_range"]["schema"]["maximum"] == 100
        assert params["demo_str_choice"]["schema"]["enum"] == ["choice1", "choice2"]
        assert params["demo_password"]["schema"]["format"] == "password"
        assert params["demo_list_of_floats"]["schema"]["type"] == "array"

    def test_files(self, client, operation):
        content = operation["requestBody"]["content"]
        ref = content["multipart/form-data"]["schema"]["$ref"].split("/")[-1]
        schema = client.get("/openapi.json").json()["components"]["schemas"][ref]
        files = {"demo_image", "demo_audio", "demo_video"}
        assert set(schema["properties"]) == files
        assert set(schema["required"]) == files
        image = schema["properties"]["demo_image"]
        assert image["format"] == "binary"
        assert image["description"] == "test image upload"

    def test_response_schema(self, client, operation):
        content = operation["responses"]["200"]["content"]["application/json"]
        ref = content["schema"]["$ref"].split("/")[-1]
        assert ref == "ModelPredictionResponse"
        schema = client.get("/openapi.json").json()["components"]["schemas"][ref]
        properties = schema["properties"]
        assert properties["demo_image"]["description"] == "image"
        assert properties["demo_password"]["format"] == "password"

    def test_media_types(self, operation):
        content = operation["responses"]["200"]["content"]
        assert {"application/json", "application/zip", "image/*"} <= set(content)


class TestCLI:
    @pytest.fixture
    def input_files(self, tmp_path):
        paths = {}
        for name, content, ext in [
            ("demo_image", IMAGE, "png"),
            ("demo_audio", AUDIO, "wav"),
            ("demo_video", VIDEO, "mp4"),
        ]:
            path = tmp_path / f"{name}.{ext}"
            path.write_bytes(content)
            paths[name] = str(path)
        return paths

    def _args(self, input_files, *extra):
        args = ["--model-name", MODEL_NAME]
        return args, ["predict", *extra] + [
            a for k, v in input_files.items() for a in (f"--{k}", v)
        ]

    def test_get_metadata(self, capsys):
        cli.main(["--model-name", MODEL_NAME, "get_metadata"])
        assert json.loads(capsys.readouterr().out)["name"] == "ai4os_demo_app"

    def test_predict(self, input_files, capsys):
        opts, predict = self._args(input_files, "--demo_int", "7")
        cli.main(opts + predict)
        data = json.loads(capsys.readouterr().out)
        assert data["demo_int"] == 7
        assert data["demo_image"] == _b64(IMAGE)

    def test_predict_image(self, input_files, tmp_path):
        out = tmp_path / "out" / "result"
        opts, predict = self._args(input_files, "--accept", "image/*")
        cli.main(opts + ["--deepaas_method_output", str(out)] + predict)
        assert (tmp_path / "out" / "result.png").read_bytes() == IMAGE

    def test_predict_zip(self, input_files, tmp_path):
        out = tmp_path / "result.zip"
        opts, predict = self._args(input_files, "--accept", "application/zip")
        cli.main(opts + ["--deepaas_method_output", str(out)] + predict)
        with zipfile.ZipFile(out) as z:
            assert "args.json" in z.namelist()
