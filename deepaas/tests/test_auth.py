# -*- coding: utf-8 -*-

# Copyright 2024 Spanish National Research Council (CSIC)
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

import fastapi
import fastapi.security
import fastapi.testclient
import pytest
from oslo_config import cfg

from deepaas import auth
from deepaas import config

CONF = cfg.CONF


class TestBearerAuth:
    def setup_method(self):
        """Set up test environment."""
        # Reset config to clean state
        CONF.clear()
        config.parse_args([])

    def test_auth_disabled_by_default(self):
        """Test that authentication is disabled by default."""
        assert not auth.is_auth_enabled()

    def test_auth_enabled_with_token(self):
        """Test that authentication is enabled when token is set."""
        CONF.set_override("auth_bearer_token", "test-token")
        assert auth.is_auth_enabled()

    @pytest.mark.asyncio
    async def test_verify_token_disabled_auth(self):
        """Test token verification when auth is disabled."""
        CONF.set_override("auth_bearer_token", "")
        result = await auth.verify_bearer_token(None)
        assert result is None

    @pytest.mark.asyncio
    async def test_verify_token_no_token_provided(self):
        """Test token verification when auth is enabled but no token provided."""
        CONF.set_override("auth_bearer_token", "test-token")
        
        with pytest.raises(fastapi.HTTPException) as exc_info:
            await auth.verify_bearer_token(None)
        
        assert exc_info.value.status_code == 401
        assert "Bearer token required" in exc_info.value.detail
        assert exc_info.value.headers["WWW-Authenticate"] == "Bearer"

    @pytest.mark.asyncio
    async def test_verify_token_invalid_token(self):
        """Test token verification with invalid token."""
        CONF.set_override("auth_bearer_token", "correct-token")
        
        # Mock HTTPAuthorizationCredentials
        mock_token = fastapi.security.HTTPAuthorizationCredentials(
            scheme="Bearer", 
            credentials="wrong-token"
        )
        
        with pytest.raises(fastapi.HTTPException) as exc_info:
            await auth.verify_bearer_token(mock_token)
        
        assert exc_info.value.status_code == 401
        assert "Invalid bearer token" in exc_info.value.detail
        assert exc_info.value.headers["WWW-Authenticate"] == "Bearer"

    @pytest.mark.asyncio
    async def test_verify_token_valid_token(self):
        """Test token verification with valid token."""
        CONF.set_override("auth_bearer_token", "correct-token")
        
        # Mock HTTPAuthorizationCredentials
        mock_token = fastapi.security.HTTPAuthorizationCredentials(
            scheme="Bearer", 
            credentials="correct-token"
        )
        
        result = await auth.verify_bearer_token(mock_token)
        assert result == "correct-token"

    def test_get_auth_dependency(self):
        """Test getting the auth dependency."""
        dependency = auth.get_auth_dependency()
        # Check that it's a fastapi.Depends object
        assert hasattr(dependency, 'dependency')
        assert callable(dependency.dependency)


class TestBearerAuthIntegration:
    """Integration tests for bearer authentication with FastAPI."""

    def setup_method(self):
        """Set up test environment."""
        CONF.clear()
        config.parse_args([])

    def create_test_app(self):
        """Create a simple FastAPI app for testing."""
        app = fastapi.FastAPI()

        @app.get("/public")
        async def public_endpoint():
            return {"message": "public"}

        @app.get("/protected")
        async def protected_endpoint(_: str = auth.get_auth_dependency()):
            return {"message": "protected"}

        return app

    def test_public_endpoint_no_auth(self):
        """Test that public endpoints work without authentication."""
        app = self.create_test_app()
        client = fastapi.testclient.TestClient(app)
        
        response = client.get("/public")
        assert response.status_code == 200
        assert response.json() == {"message": "public"}

    def test_protected_endpoint_no_auth_disabled(self):
        """Test protected endpoint when auth is disabled."""
        CONF.set_override("auth_bearer_token", "")
        app = self.create_test_app()
        client = fastapi.testclient.TestClient(app)
        
        response = client.get("/protected")
        assert response.status_code == 200
        assert response.json() == {"message": "protected"}

    def test_protected_endpoint_auth_enabled_no_token(self):
        """Test protected endpoint when auth is enabled but no token provided."""
        CONF.set_override("auth_bearer_token", "secret-token")
        app = self.create_test_app()
        client = fastapi.testclient.TestClient(app)
        
        response = client.get("/protected")
        assert response.status_code == 401
        assert "Bearer token required" in response.json()["detail"]

    def test_protected_endpoint_auth_enabled_invalid_token(self):
        """Test protected endpoint with invalid token."""
        CONF.set_override("auth_bearer_token", "secret-token")
        app = self.create_test_app()
        client = fastapi.testclient.TestClient(app)
        
        response = client.get(
            "/protected",
            headers={"Authorization": "Bearer wrong-token"}
        )
        assert response.status_code == 401
        assert "Invalid bearer token" in response.json()["detail"]

    def test_protected_endpoint_auth_enabled_valid_token(self):
        """Test protected endpoint with valid token."""
        CONF.set_override("auth_bearer_token", "secret-token")
        app = self.create_test_app()
        client = fastapi.testclient.TestClient(app)
        
        response = client.get(
            "/protected",
            headers={"Authorization": "Bearer secret-token"}
        )
        assert response.status_code == 200
        assert response.json() == {"message": "protected"}

    def test_protected_endpoint_malformed_header(self):
        """Test protected endpoint with malformed Authorization header."""
        CONF.set_override("auth_bearer_token", "secret-token")
        app = self.create_test_app()
        client = fastapi.testclient.TestClient(app)
        
        # Test with malformed header (no "Bearer" prefix)
        response = client.get(
            "/protected",
            headers={"Authorization": "secret-token"}
        )
        assert response.status_code == 401
        assert "Bearer token required" in response.json()["detail"]