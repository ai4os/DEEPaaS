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

"""Tests for the bearer token authentication."""

import io

import fastapi
import fastapi.security
import pytest

from deepaas import auth
from deepaas import config
from deepaas.tests.conftest import TEST_MODEL_NAME

TOKEN = "s3cr3t-t0k3n"  # nosec

PROTECTED = [
    ("GET", "/v2/models/"),
    ("GET", f"/v2/models/{TEST_MODEL_NAME}"),
    ("POST", f"/v2/models/{TEST_MODEL_NAME}/predict"),
    ("GET", "/v2/debug/"),
]

PUBLIC = [
    ("GET", "/"),
    ("GET", "/v2/"),
    ("GET", "/openapi.json"),
    ("GET", "/swagger.json"),
    ("GET", "/docs"),
    ("GET", "/redoc"),
]


@pytest.fixture
def token(monkeypatch):
    monkeypatch.setattr(config.CONF, "auth_bearer_token", TOKEN)
    return TOKEN


def _request(client, method, path, headers=None):
    kwargs = {"headers": headers or {}}
    if method == "POST":
        kwargs["files"] = {"data": ("test.bin", io.BytesIO(b"dummy"), "text/plain")}
        kwargs["data"] = {"parameter": "1"}
    return client.request(method, path, **kwargs)


def _credentials(token):
    return fastapi.security.HTTPAuthorizationCredentials(
        scheme="Bearer", credentials=token
    )


class TestVerifyBearerToken:
    def test_auth_disabled_by_default(self):
        assert not auth.is_auth_enabled()

    def test_auth_enabled(self, token):
        assert auth.is_auth_enabled()

    async def test_disabled_allows_requests(self):
        assert await auth.verify_bearer_token(None) is None
        assert await auth.verify_bearer_token(_credentials("foo")) is None

    async def test_missing_token(self, token):
        with pytest.raises(fastapi.HTTPException) as e:
            await auth.verify_bearer_token(None)
        assert e.value.status_code == 401
        assert e.value.headers == {"WWW-Authenticate": "Bearer"}

    @pytest.mark.parametrize("value", ["", "wrong", TOKEN + "x", TOKEN[:-1], "ñ"])
    async def test_invalid_token(self, token, value):
        with pytest.raises(fastapi.HTTPException) as e:
            await auth.verify_bearer_token(_credentials(value))
        assert e.value.status_code == 401

    async def test_valid_token(self, token):
        assert await auth.verify_bearer_token(_credentials(TOKEN)) == TOKEN


class TestAPIAuthentication:
    @pytest.mark.parametrize("method,path", PROTECTED + PUBLIC)
    def test_auth_disabled(self, client, method, path):
        r = _request(client, method, path)
        assert r.status_code in (200, 204)

    @pytest.mark.parametrize("method,path", PROTECTED)
    def test_protected_without_token(self, client, token, method, path):
        r = _request(client, method, path)
        assert r.status_code == 401
        assert r.headers["www-authenticate"] == "Bearer"

    @pytest.mark.parametrize("method,path", PROTECTED)
    @pytest.mark.parametrize(
        "header",
        ["Bearer wrong", f"Basic {TOKEN}", TOKEN, "Bearer"],
    )
    def test_protected_with_invalid_token(self, client, token, method, path, header):
        r = _request(client, method, path, headers={"Authorization": header})
        assert r.status_code == 401

    @pytest.mark.parametrize("method,path", PROTECTED)
    def test_protected_with_valid_token(self, client, token, method, path):
        r = _request(client, method, path, headers={"Authorization": f"Bearer {TOKEN}"})
        assert r.status_code in (200, 204)

    @pytest.mark.parametrize("method,path", PUBLIC)
    def test_public_without_token(self, client, token, method, path):
        r = _request(client, method, path)
        assert r.status_code == 200

    def test_openapi_declares_security(self, client):
        spec = client.get("/openapi.json").json()
        assert "HTTPBearer" in spec["components"]["securitySchemes"]
        for method, path in PROTECTED:
            op = spec["paths"][path][method.lower()]
            assert op["security"] == [{"HTTPBearer": []}]
