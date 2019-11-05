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

import marshmallow
from marshmallow import fields
from marshmallow import validate


class Location(marshmallow.Schema):
    rel = fields.Str(required=True)
    href = fields.Url(required=True)


class Version(marshmallow.Schema):
    version = fields.Str(required="True")
    id = fields.Str(required="True")
    link = fields.Nested(Location)
    type = fields.Str()


class Versions(marshmallow.Schema):
    versions = fields.List(fields.Nested(Version))


class Failure(marshmallow.Schema):
    message = fields.Str(required=True,
                         description="Failure message")


class Prediction(marshmallow.Schema):
    status = fields.String(required=True,
                           description='Response status message')
    predictions = fields.Str(required=True,
                             description='String containing predictions')


class ModelMeta(marshmallow.Schema):
    id =  fields.Str(required=True, description='Model identifier')  # noqa
    name = fields.Str(required=True, description='Model name')
    description = fields.Str(required=True,
                             description='Model description')
    license = fields.Str(required=False, description='Model license')
    author = fields.Str(required=False, description='Model author')
    version = fields.Str(required=False, description='Model version')
    url = fields.Str(required=False, description='Model url')
    links = fields.List(fields.Nested(Location))


class Training(marshmallow.Schema):
    uuid = fields.UUID(required=True, description='Training identifier')
    date = fields.DateTime(required=True, description='Training start time')
    status = fields.Str(
        required=True,
        description='Training status',
        enum=["running", "error", "completed", "cancelled"],
        validate=validate.OneOf(["running", "error", "completed", "cancelled"])
    )
    message = fields.Str(description="Optional message explaining status")


class TrainingList(marshmallow.Schema):
    trainings = fields.List(fields.Nested(Training))
