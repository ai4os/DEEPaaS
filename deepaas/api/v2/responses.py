# -*- coding: utf-8 -*-

# Copyright 2019 Spanish National Research Council (CSIC)
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

import typing

import marshmallow
from marshmallow import fields
from marshmallow import validate
import pydantic


# class Version(marshmallow.Schema):
#     version = fields.Str(required="True")
#     id = fields.Str(required="True")
#     # links = fields.Nested(Location)
#     type = fields.Str()


# class Versions(marshmallow.Schema):
#     versions = fields.List(fields.Nested(Version))


class Failure(marshmallow.Schema):
    message = fields.Str(required=True, description="Failure message")


class Prediction(marshmallow.Schema):
    status = fields.String(required=True, description="Response status message")
    predictions = fields.Str(required=True, description="String containing predictions")


class Training(marshmallow.Schema):
    uuid = fields.UUID(required=True, description="Training identifier")
    date = fields.DateTime(required=True, description="Training start time")
    status = fields.Str(
        required=True,
        description="Training status",
        enum=["running", "error", "completed", "cancelled"],
        validate=validate.OneOf(["running", "error", "completed", "cancelled"]),
    )
    message = fields.Str(description="Optional message explaining status")


class TrainingList(marshmallow.Schema):
    trainings = fields.List(fields.Nested(Training))


# Pydantic models for the API


class Location(pydantic.BaseModel):
    rel: str
    href: pydantic.AnyHttpUrl
    type: str = "application/json"


class ModelMeta(pydantic.BaseModel):
    """"V2 model metadata.

    This class is used to represent the metadata of a model in the V2 API, as we were
    doing in previous versions.
    """
    id: str = pydantic.Field(..., description="Model identifier")  # noqa
    name: str = pydantic.Field(..., description="Model name")
    description: typing.Optional[str] = pydantic.Field(
        description="Model description",
        default=None
    )
    summary: typing.Optional[str] = pydantic.Field(
        description="Model summary",
        default=None
    )
    license: typing.Optional[str] = pydantic.Field(
        description="Model license",
        default=None
    )
    author: typing.Optional[str] = pydantic.Field(
        description="Model author",
        default=None
    )
    version: typing.Optional[str] = pydantic.Field(
        description="Model version",
        default=None
    )
    url: typing.Optional[str] = pydantic.Field(
        description="Model url",
        default=None
    )
    # Links can be alist of Locations, or an empty list
    links: typing.List[Location] = pydantic.Field(
        description="Model links",
    )


class ModelList(pydantic.BaseModel):
    models: typing.List[ModelMeta] = pydantic.Field(
        ...,
        description="List of loaded models"
    )
