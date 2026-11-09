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

"""Bearer token authentication for the DEEPaaS API."""

import secrets
import typing

import fastapi
import fastapi.security

from deepaas import config
from deepaas import log

CONF = config.CONF
LOG = log.getLogger(__name__)

# NOTE(aloga): auto_error is disabled so that we can allow requests without
# credentials when authentication is not enabled, and return a 401 (instead of
# a 403) when it is.
bearer_scheme = fastapi.security.HTTPBearer(
    auto_error=False,
    description="Bearer token, needed if the API has been started with a token.",
)


def is_auth_enabled() -> bool:
    """Check if authentication is enabled."""
    return bool(CONF.auth_bearer_token)


def _unauthorized(detail: str) -> fastapi.HTTPException:
    return fastapi.HTTPException(
        status_code=401,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


_bearer_credentials = fastapi.Depends(bearer_scheme)


async def verify_bearer_token(
    credentials: typing.Optional[
        fastapi.security.HTTPAuthorizationCredentials
    ] = _bearer_credentials,
) -> typing.Optional[str]:
    """Verify the bearer token of the request against the configured one.

    :param credentials: credentials sent in the ``Authorization`` header.
    :returns: the validated token, or ``None`` if authentication is disabled.
    :raises fastapi.HTTPException: if authentication is enabled and the token
        is missing or invalid.
    """
    if not is_auth_enabled():
        return None

    if credentials is None:
        LOG.warning("Authentication required but no bearer token provided")
        raise _unauthorized("Bearer token required")

    # Use a constant time comparison to prevent timing attacks
    if not secrets.compare_digest(
        credentials.credentials.encode("utf-8"),
        CONF.auth_bearer_token.encode("utf-8"),
    ):
        LOG.warning("Invalid bearer token provided")
        raise _unauthorized("Invalid bearer token")

    return credentials.credentials


def get_auth_dependency() -> typing.Any:
    """Get the dependency that enforces authentication when it is enabled."""
    return fastapi.Depends(verify_bearer_token)
