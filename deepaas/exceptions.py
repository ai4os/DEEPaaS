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

import fastapi


# Exceptions that are handled  at the CLI application level (i.e. those that prevent the
# API from starting.


class ModuleNotFoundError(Exception):
    """Module not found error."""


class NoModelsAvailable(Exception):
    """No models are available in the system."""


class MultipleModelsFound(Exception):
    """Multiple models found."""


# Exceptions that are handled at the API level (i.e. those that are returned to the
# user). These extend the FastAPI HTTPException class.


class BaseHTTPError(fastapi.HTTPException):
    """Base HTTP errors."""

    detail = "ERROR"
    status_code = 500

    def __init__(self, status_code: int = None, detail: str = None):
        super().__init__(
            status_code=status_code or self.status_code, detail=detail or self.detail
        )


class MissingModelSchemaError(BaseHTTPError):
    """Missing model schema error."""

    detail = "ERROR trying to validate model schema without an schema defined."
    status_code = 500


class ModelResponseValidationError(BaseHTTPError):
    """Model response validation error."""

    detail = "ERROR validating model response. Check server logs for more information."
    status_code = 500


class ModelInputValidationError(BaseHTTPError):
    """Model input validation error."""

    detail = "ERROR validating model input. Check server logs for more information."
    status_code = 400


class ModelMethodNotImplementedError(BaseHTTPError):
    """Model method not implemented error."""

    detail = "ERROR: method not implemented."
    status_code = 501


class ModelMethodUnexpectedError(BaseHTTPError):
    """Model method unexpected error."""

    detail = "ERROR: unexpected error."
    status_code = 500

    def __init__(self, detail: str = None, reason: Exception = None):
        detail = f"{detail or self.detail}: {reason}"

        super().__init__(status_code=self.status_code, detail=detail)
