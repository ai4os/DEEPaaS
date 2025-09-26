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
from oslo_config import cfg

from deepaas import log

CONF = cfg.CONF
LOG = log.getLogger(__name__)

# HTTP Bearer security scheme for FastAPI
bearer_scheme = fastapi.security.HTTPBearer(auto_error=False)


def is_auth_enabled() -> bool:
    """Check if authentication is enabled."""
    return bool(CONF.auth_bearer_token)


async def verify_bearer_token(
    token: fastapi.security.HTTPAuthorizationCredentials = fastapi.Depends(bearer_scheme)  # noqa: E501,B008
) -> str:
    """Verify the bearer token against the configured token.

    :param token: The HTTPAuthorizationCredentials from the request
    :type token: fastapi.security.HTTPAuthorizationCredentials

    :returns: The validated token string
    :rtype: str

    :raises HTTPException: If authentication is enabled but token is invalid/missing
    """
    # If auth is not enabled, allow all requests
    if not is_auth_enabled():
        return None

    # If auth is enabled but no token provided
    if token is None:
        LOG.warning("Authentication required but no bearer token provided")
        raise fastapi.HTTPException(
            status_code=401,
            detail="Bearer token required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Validate the token
    if token.credentials != CONF.auth_bearer_token:
        LOG.warning("Invalid bearer token provided")
        raise fastapi.HTTPException(
            status_code=401,
            detail="Invalid bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    LOG.debug("Bearer token validated successfully")
    return token.credentials


def get_auth_dependency():
    """Get the authentication dependency.

    Returns a dependency that can be used with FastAPI routes to enforce
    authentication when enabled.

    :returns: The authentication dependency function
    :rtype: fastapi.Depends
    """
    return fastapi.Depends(verify_bearer_token)
