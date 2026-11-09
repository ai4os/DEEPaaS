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

"""Integration tests for the FastAPI-based DEEPaaS v2 API endpoints.

These tests exercise the full HTTP stack using a ``TestClient`` backed by a
real FastAPI application loaded with the ``fake_v2_model.TestModel`` dummy
model.  The ``client`` fixture is provided by ``conftest.py``.
"""

import io
import os

import fastapi
from marshmallow import fields as m_fields
from marshmallow import validate
import pytest
import starlette.datastructures

from deepaas.api.v2 import predict as v2_predict
from deepaas import model
from deepaas.model.v2 import wrapper as v2_wrapper
from deepaas.tests.conftest import TEST_MODEL_NAME

# ---------------------------------------------------------------------------
# Root version endpoint
# ---------------------------------------------------------------------------


class TestRootEndpoint:
    """Tests for ``GET /``."""

    def test_get_root_status(self, client):
        r = client.get("/")
        assert r.status_code == 200

    def test_get_root_has_versions(self, client):
        data = client.get("/").json()
        assert "versions" in data
        assert isinstance(data["versions"], list)
        assert len(data["versions"]) >= 1

    def test_get_root_has_v2_version(self, client):
        versions = client.get("/").json()["versions"]
        ids = [v["id"] for v in versions]
        assert "v2" in ids

    def test_get_root_has_links(self, client):
        data = client.get("/").json()
        assert "links" in data
        assert isinstance(data["links"], list)

    def test_get_root_links_include_openapi(self, client):
        links = client.get("/").json()["links"]
        hrefs = [link["href"] for link in links]
        assert any("openapi.json" in href for href in hrefs)

    def test_get_root_links_include_docs(self, client):
        links = client.get("/").json()["links"]
        hrefs = [link["href"] for link in links]
        assert any("docs" in href for href in hrefs)


# ---------------------------------------------------------------------------
# V2 version endpoint
# ---------------------------------------------------------------------------


class TestV2VersionEndpoint:
    """Tests for ``GET /v2/``."""

    def test_get_v2_status(self, client):
        r = client.get("/v2/")
        assert r.status_code == 200

    def test_get_v2_id(self, client):
        data = client.get("/v2/").json()
        assert data["id"] == "v2"

    def test_get_v2_version_stable(self, client):
        data = client.get("/v2/").json()
        assert data["version"] == "stable"

    def test_get_v2_has_links(self, client):
        data = client.get("/v2/").json()
        assert "links" in data
        assert len(data["links"]) >= 1

    def test_get_v2_self_link(self, client):
        data = client.get("/v2/").json()
        rels = [link["rel"] for link in data["links"]]
        assert "self" in rels


# ---------------------------------------------------------------------------
# Models list endpoint
# ---------------------------------------------------------------------------


class TestModelsListEndpoint:
    """Tests for ``GET /v2/models/``."""

    def test_get_models_status(self, client):
        r = client.get("/v2/models/")
        assert r.status_code == 200

    def test_get_models_has_models_key(self, client):
        data = client.get("/v2/models/").json()
        assert "models" in data

    def test_get_models_returns_list(self, client):
        data = client.get("/v2/models/").json()
        assert isinstance(data["models"], list)

    def test_get_models_contains_test_model(self, client):
        data = client.get("/v2/models/").json()
        names = [m["name"] for m in data["models"]]
        assert TEST_MODEL_NAME in names

    def test_get_models_metadata_fields(self, client):
        data = client.get("/v2/models/").json()
        model = data["models"][0]
        for key in ("id", "name", "links"):
            assert key in model

    def test_get_models_self_link(self, client):
        data = client.get("/v2/models/").json()
        model = data["models"][0]
        rels = [link["rel"] for link in model["links"]]
        assert "self" in rels


# ---------------------------------------------------------------------------
# Single model metadata endpoint
# ---------------------------------------------------------------------------


class TestModelMetaEndpoint:
    """Tests for ``GET /v2/models/{model_name}``."""

    def test_get_model_status(self, client):
        r = client.get(f"/v2/models/{TEST_MODEL_NAME}")
        assert r.status_code == 200

    def test_get_model_name(self, client):
        data = client.get(f"/v2/models/{TEST_MODEL_NAME}").json()
        assert data["name"] == TEST_MODEL_NAME

    def test_get_model_has_description(self, client):
        data = client.get(f"/v2/models/{TEST_MODEL_NAME}").json()
        assert "description" in data
        assert data["description"] is not None

    def test_get_model_has_author(self, client):
        data = client.get(f"/v2/models/{TEST_MODEL_NAME}").json()
        assert data.get("author") == "Alvaro Lopez Garcia"

    def test_get_model_has_links(self, client):
        data = client.get(f"/v2/models/{TEST_MODEL_NAME}").json()
        assert "links" in data
        assert len(data["links"]) >= 1

    def test_get_model_self_link_points_to_model(self, client):
        data = client.get(f"/v2/models/{TEST_MODEL_NAME}").json()
        self_links = [link["href"] for link in data["links"] if link["rel"] == "self"]
        assert len(self_links) >= 1
        assert TEST_MODEL_NAME in self_links[0]

    def test_get_unknown_model_returns_404(self, client):
        r = client.get("/v2/models/nonexistent-model")
        assert r.status_code == 404


# ---------------------------------------------------------------------------
# Predict endpoint
# ---------------------------------------------------------------------------


class TestPredictEndpoint:
    """Tests for ``POST /v2/models/{model_name}/predict``."""

    @pytest.fixture()
    def upload_file(self):
        return ("test.bin", io.BytesIO(b"dummy content"), "application/octet-stream")

    def test_predict_status(self, client, upload_file):
        r = client.post(
            f"/v2/models/{TEST_MODEL_NAME}/predict",
            files={"data": upload_file},
            data={"parameter": "1"},
        )
        assert r.status_code == 200

    def test_predict_response_has_expected_keys(self, client, upload_file):
        r = client.post(
            f"/v2/models/{TEST_MODEL_NAME}/predict",
            files={"data": upload_file},
            data={"parameter": "1"},
        )
        data = r.json()
        # The fake model returns date / labels / data
        assert "date" in data
        assert "labels" in data

    def test_predict_labels_structure(self, client, upload_file):
        r = client.post(
            f"/v2/models/{TEST_MODEL_NAME}/predict",
            files={"data": upload_file},
            data={"parameter": "1"},
        )
        labels = r.json()["labels"]
        assert isinstance(labels, list)
        assert labels[0]["label"] == "foo"
        assert labels[0]["probability"] == 1.0

    def test_predict_with_optional_parameter(self, client, upload_file):
        r = client.post(
            f"/v2/models/{TEST_MODEL_NAME}/predict",
            files={"data": upload_file},
            data={"parameter": "1", "parameter_three": "foo"},
        )
        assert r.status_code == 200

    def test_predict_missing_required_file_returns_422(self, client):
        r = client.post(
            f"/v2/models/{TEST_MODEL_NAME}/predict",
            data={"parameter": "1"},
        )
        assert r.status_code == 422

    def test_predict_missing_required_parameter_returns_422(self, client, upload_file):
        r = client.post(
            f"/v2/models/{TEST_MODEL_NAME}/predict",
            files={"data": upload_file},
        )
        assert r.status_code == 422

    def test_predict_invalid_model_returns_404(self, client, upload_file):
        r = client.post(
            "/v2/models/nonexistent/predict",
            files={"data": upload_file},
            data={"parameter": "1"},
        )
        assert r.status_code == 404


# ---------------------------------------------------------------------------
# Debug endpoint
# ---------------------------------------------------------------------------


class TestDebugEndpoint:
    """Tests for ``GET /v2/debug/``."""

    def test_debug_disabled_returns_204(self, client):
        # Debug is not enabled in the test app, so we expect 204 No Content.
        r = client.get("/v2/debug/")
        assert r.status_code == 204


# ---------------------------------------------------------------------------
# OpenAPI / Swagger spec endpoints
# ---------------------------------------------------------------------------


class TestSpecEndpoints:
    """Tests for the OpenAPI schema and Swagger compatibility endpoints."""

    def test_openapi_json_status(self, client):
        r = client.get("/openapi.json")
        assert r.status_code == 200

    def test_openapi_json_structure(self, client):
        data = client.get("/openapi.json").json()
        for key in ("openapi", "info", "paths"):
            assert key in data

    def test_openapi_json_contains_v2_paths(self, client):
        paths = client.get("/openapi.json").json()["paths"]
        assert any("/v2/" in p for p in paths)

    def test_swagger_json_compatibility(self, client):
        """``/swagger.json`` must redirect / proxy to the OpenAPI spec."""
        r = client.get("/swagger.json")
        assert r.status_code == 200
        data = r.json()
        assert "paths" in data

    def test_docs_endpoint_accessible(self, client):
        r = client.get("/docs")
        assert r.status_code == 200

    def test_redoc_endpoint_accessible(self, client):
        r = client.get("/redoc")
        assert r.status_code == 200


# ---------------------------------------------------------------------------
# Uploaded files
# ---------------------------------------------------------------------------


class TestUploadedFiles:
    """Uploaded files must reach the model as ``UploadedFile`` objects."""

    def test_save_uploaded_files(self):
        upload = starlette.datastructures.UploadFile(
            io.BytesIO(b"some content"),
            filename="original.txt",
            headers=starlette.datastructures.Headers({"content-type": "text/plain"}),
        )
        kwargs, tmp_files = v2_predict._save_uploaded_files(
            {"data": upload, "parameter": 1}
        )
        try:
            assert kwargs["parameter"] == 1
            f = kwargs["data"]
            assert isinstance(f, v2_wrapper.UploadedFile)
            assert f.name == "data"
            assert f.content_type == "text/plain"
            assert f.original_filename == "original.txt"
            assert tmp_files == [f.filename]
            with open(f.filename, "rb") as fd:
                assert fd.read() == b"some content"
        finally:
            v2_predict._remove_files(tmp_files)
        assert not os.path.exists(f.filename)

    def test_remove_files_ignores_missing(self, tmp_path):
        v2_predict._remove_files([str(tmp_path / "does-not-exist")])

    def test_model_receives_uploaded_file(self, client, monkeypatch):
        received = {}

        def predict(**kwargs):
            f = kwargs["data"]
            received["data"] = f
            received["exists"] = os.path.exists(f.filename)
            with open(f.filename, "rb") as fd:
                received["content"] = fd.read()
            return {"date": "2019-01-1", "labels": []}

        monkeypatch.setattr(model.V2_MODEL.model_obj, "predict", predict)

        r = client.post(
            f"/v2/models/{TEST_MODEL_NAME}/predict",
            files={"data": ("test.bin", io.BytesIO(b"dummy"), "text/plain")},
            data={"parameter": "1"},
        )
        assert r.status_code == 200
        f = received["data"]
        assert isinstance(f, v2_wrapper.UploadedFile)
        assert f.original_filename == "test.bin"
        assert f.content_type == "text/plain"
        assert received["exists"]
        assert received["content"] == b"dummy"
        # Temporary files are removed once the response has been sent
        assert not os.path.exists(f.filename)

    def test_tmp_files_removed_on_error(self, client, monkeypatch):
        received = {}

        def predict(**kwargs):
            received["data"] = kwargs["data"]
            raise Exception("model error")

        monkeypatch.setattr(model.V2_MODEL.model_obj, "predict", predict)

        r = client.post(
            f"/v2/models/{TEST_MODEL_NAME}/predict",
            files={"data": ("test.bin", io.BytesIO(b"dummy"), "text/plain")},
            data={"parameter": "1"},
        )
        assert r.status_code == 500
        assert not os.path.exists(received["data"].filename)


# ---------------------------------------------------------------------------
# Accept header and returned files
# ---------------------------------------------------------------------------


class TestAcceptNegotiation:
    """The ``accept`` argument is taken from the ``Accept`` header."""

    choices = ["application/json", "text/plain", "image/png"]

    @pytest.mark.parametrize(
        "header,expected",
        [
            (None, "application/json"),
            ("", "application/json"),
            ("*/*", "application/json"),
            ("text/plain", "text/plain"),
            ("image/png;q=0.9", "image/png"),
            ("text/html, image/png, */*", "image/png"),
            ("text/html, */*;q=0.8", "application/json"),
        ],
    )
    def test_negotiate(self, header, expected):
        assert (
            v2_predict._negotiate_accept(header, self.choices, "application/json")
            == expected
        )

    def test_negotiate_not_acceptable(self):
        with pytest.raises(fastapi.HTTPException) as e:
            v2_predict._negotiate_accept("text/html", self.choices, "application/json")
        assert e.value.status_code == 406

    def test_negotiate_no_choices(self):
        assert v2_predict._negotiate_accept("text/html", [], "foo/bar") == "text/html"

    def test_accept_choices_and_default(self):
        field = m_fields.Str(
            load_default="image/png",
            validate=validate.OneOf(["application/json", "image/png"]),
        )
        choices, default = v2_predict._get_accept_choices(field)
        assert choices == ["application/json", "image/png"]
        assert default == "image/png"

    def test_accept_choices_first_as_default(self):
        field = m_fields.Str(validate=[validate.OneOf(["text/plain", "image/png"])])
        assert v2_predict._get_accept_choices(field) == (
            ["text/plain", "image/png"],
            "text/plain",
        )

    @pytest.mark.parametrize(
        "accept,filename,expected",
        [
            ("image/png", None, "image/png"),
            ("image/*", "foo.jpg", "image/jpeg"),
            ("image/*", "foo", "application/octet-stream"),
            ("image/*", None, "application/octet-stream"),
        ],
    )
    def test_get_media_type(self, accept, filename, expected):
        assert v2_predict._get_media_type(accept, filename) == expected


class TestPredictResponses:
    """Responses depending on the ``Accept`` header and the model output."""

    url = f"/v2/models/{TEST_MODEL_NAME}/predict"

    def _post(self, client, **kwargs):
        return client.post(
            self.url,
            files={"data": ("test.bin", io.BytesIO(b"dummy"), "text/plain")},
            data={"parameter": "1"},
            **kwargs,
        )

    def test_accept_any_returns_json(self, client):
        r = self._post(client, headers={"accept": "*/*"})
        assert r.status_code == 200
        assert r.headers["content-type"] == "application/json"
        assert "labels" in r.json()

    def test_accept_text_plain(self, client):
        r = self._post(client, headers={"accept": "text/plain"})
        assert r.status_code == 200
        assert r.headers["content-type"].startswith("text/plain")
        assert r.text.startswith("data:image/png;base64,")

    def test_accept_image_png(self, client):
        r = self._post(client, headers={"accept": "image/png"})
        assert r.status_code == 200
        assert r.headers["content-type"] == "image/png"
        assert r.content.startswith(b"\x89PNG")

    def test_accept_not_supported(self, client):
        r = self._post(client, headers={"accept": "text/html"})
        assert r.status_code == 406

    def test_model_receives_accept(self, client, monkeypatch):
        received = {}

        def predict(**kwargs):
            received.update(kwargs)
            return {"date": "2019-01-1", "labels": []}

        monkeypatch.setattr(model.V2_MODEL.model_obj, "predict", predict)
        self._post(client, headers={"accept": "*/*"})
        assert received["accept"] == "application/json"

    def test_returned_file(self, client, monkeypatch, tmp_path):
        path = tmp_path / "result.png"
        path.write_bytes(b"\x89PNG result")

        def predict(**kwargs):
            return open(path, "rb")

        monkeypatch.setattr(model.V2_MODEL.model_obj, "predict", predict)
        r = self._post(client, headers={"accept": "image/png"})
        assert r.status_code == 200
        assert r.headers["content-type"] == "image/png"
        assert r.content == b"\x89PNG result"

    def test_return_uploaded_file(self, client, monkeypatch):
        def predict(**kwargs):
            return open(kwargs["data"].filename, "rb")

        monkeypatch.setattr(model.V2_MODEL.model_obj, "predict", predict)
        r = self._post(client, headers={"accept": "image/png"})
        assert r.status_code == 200
        assert r.content == b"dummy"

    def test_openapi_documents_media_types(self, client):
        spec = client.get("/openapi.json").json()
        content = spec["paths"][self.url]["post"]["responses"]["200"]["content"]
        assert {"application/json", "text/plain", "image/png"} <= set(content)
        assert "accept" not in [
            p["name"] for p in spec["paths"][self.url]["post"].get("parameters", [])
        ]
