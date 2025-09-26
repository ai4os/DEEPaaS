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

"""End-to-end tests for bearer authentication in the API."""

import unittest.mock
import fastapi.testclient
from oslo_config import cfg

from deepaas import api
from deepaas import config
from deepaas import model

CONF = cfg.CONF


class TestE2EBearerAuth:
    """End-to-end tests for bearer authentication."""
    
    def setup_method(self):
        """Set up test environment."""
        CONF.clear()
        config.parse_args([])
        
        # Reset the global APP
        api.APP = None

    def create_mock_model(self):
        """Create a mock model for testing."""
        mock_model = unittest.mock.MagicMock()
        mock_model.get_metadata.return_value = {
            "name": "Test Model",
            "version": "1.0.0",
            "description": "A test model",
            "author": "Test Author",
        }
        mock_model.get_predict_args.return_value = {}
        mock_model.predict = unittest.mock.AsyncMock(return_value={"result": "success"})
        mock_model.has_schema = False
        mock_model.response_schema = None  # Important: set response_schema to None
        mock_model.warm = unittest.mock.MagicMock()
        return mock_model

    def test_api_access_without_auth(self):
        """Test API access when authentication is disabled."""
        CONF.set_override("auth_bearer_token", "")
        
        with unittest.mock.patch('deepaas.model.load_v2_model') as mock_load:
            with unittest.mock.patch.object(model, 'V2_MODEL_NAME', 'test-model'):
                with unittest.mock.patch.object(model, 'V2_MODEL', self.create_mock_model()):
                    app = api.get_fastapi_app()
                    client = fastapi.testclient.TestClient(app)
                    
                    # Test root endpoint
                    response = client.get("/")
                    assert response.status_code == 200
                    
                    # Test v2 version endpoint
                    response = client.get("/v2/")
                    assert response.status_code == 200
                    
                    # Test models endpoint
                    response = client.get("/v2/models/")
                    assert response.status_code == 200
                    
                    # Test individual model endpoint
                    response = client.get("/v2/models/test-model")
                    assert response.status_code == 200

    def test_api_access_with_auth_no_token(self):
        """Test API access when authentication is enabled but no token provided."""
        CONF.set_override("auth_bearer_token", "my-secret-token")
        
        with unittest.mock.patch('deepaas.model.load_v2_model') as mock_load:
            with unittest.mock.patch.object(model, 'V2_MODEL_NAME', 'test-model'):
                with unittest.mock.patch.object(model, 'V2_MODEL', self.create_mock_model()):
                    app = api.get_fastapi_app()
                    client = fastapi.testclient.TestClient(app)
                    
                    # Test root endpoint (should still work - not protected)
                    response = client.get("/")
                    assert response.status_code == 200
                    
                    # Test v2 version endpoint (should still work - not protected)
                    response = client.get("/v2/")
                    assert response.status_code == 200
                    
                    # Test models endpoint (should require auth)
                    response = client.get("/v2/models/")
                    assert response.status_code == 401
                    assert "Bearer token required" in response.json()["detail"]
                    
                    # Test individual model endpoint (should require auth)
                    response = client.get("/v2/models/test-model")
                    assert response.status_code == 401
                    assert "Bearer token required" in response.json()["detail"]

    def test_api_access_with_auth_invalid_token(self):
        """Test API access with invalid bearer token."""
        CONF.set_override("auth_bearer_token", "my-secret-token")
        
        with unittest.mock.patch('deepaas.model.load_v2_model') as mock_load:
            with unittest.mock.patch.object(model, 'V2_MODEL_NAME', 'test-model'):
                with unittest.mock.patch.object(model, 'V2_MODEL', self.create_mock_model()):
                    app = api.get_fastapi_app()
                    client = fastapi.testclient.TestClient(app)
                    
                    headers = {"Authorization": "Bearer wrong-token"}
                    
                    # Test models endpoint with wrong token
                    response = client.get("/v2/models/", headers=headers)
                    assert response.status_code == 401
                    assert "Invalid bearer token" in response.json()["detail"]
                    
                    # Test individual model endpoint with wrong token
                    response = client.get("/v2/models/test-model", headers=headers)
                    assert response.status_code == 401
                    assert "Invalid bearer token" in response.json()["detail"]

    def test_api_access_with_auth_valid_token(self):
        """Test API access with valid bearer token."""
        CONF.set_override("auth_bearer_token", "my-secret-token")
        
        with unittest.mock.patch('deepaas.model.load_v2_model') as mock_load:
            with unittest.mock.patch.object(model, 'V2_MODEL_NAME', 'test-model'):
                with unittest.mock.patch.object(model, 'V2_MODEL', self.create_mock_model()):
                    app = api.get_fastapi_app()
                    client = fastapi.testclient.TestClient(app)
                    
                    headers = {"Authorization": "Bearer my-secret-token"}
                    
                    # Test models endpoint with correct token
                    response = client.get("/v2/models/", headers=headers)
                    assert response.status_code == 200
                    data = response.json()
                    assert "models" in data
                    assert len(data["models"]) == 1
                    assert data["models"][0]["name"] == "Test Model"
                    
                    # Test individual model endpoint with correct token
                    response = client.get("/v2/models/test-model", headers=headers)
                    assert response.status_code == 200
                    data = response.json()
                    assert data["name"] == "Test Model"
                    assert data["version"] == "1.0.0"

    def test_predict_endpoint_with_auth(self):
        """Test predict endpoint with authentication."""
        CONF.set_override("auth_bearer_token", "my-secret-token")
        
        with unittest.mock.patch('deepaas.model.load_v2_model') as mock_load:
            with unittest.mock.patch.object(model, 'V2_MODEL_NAME', 'test-model'):
                with unittest.mock.patch.object(model, 'V2_MODEL', self.create_mock_model()):
                    app = api.get_fastapi_app()
                    client = fastapi.testclient.TestClient(app)
                    
                    # Test predict endpoint without auth
                    response = client.post("/v2/models/test-model/predict")
                    assert response.status_code == 401
                    assert "Bearer token required" in response.json()["detail"]
                    
                    # Test predict endpoint with correct auth
                    headers = {"Authorization": "Bearer my-secret-token"}
                    response = client.post("/v2/models/test-model/predict", headers=headers)
                    assert response.status_code == 200
                    data = response.json()
                    assert "predictions" in data or "result" in data