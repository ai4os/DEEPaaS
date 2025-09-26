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

import datetime
import decimal
import typing

import fastapi
import marshmallow
import marshmallow.fields
import pydantic
import pydantic.utils


# Convert marshmallow fields to pydantic fields


CUSTOM_FIELD_DEFAULT = typing.Any


def get_dict_type(x):
    """For dicts we need to look at the key and value type"""
    key_type = get_pydantic_type(x.key_field)
    if x.value_field:
        value_type = get_pydantic_type(x.value_field)
        return typing.Dict[key_type, value_type]
    return typing.Dict[key_type, typing.Any]


def get_list_type(x):
    """For lists we need to look at the value type"""
    if x.inner:
        c_type = get_pydantic_type(x.inner, optional=False)
        return typing.List[c_type]
    return typing.List


FIELD_CONVERTERS = {
    marshmallow.fields.Bool: bool,
    marshmallow.fields.Boolean: bool,
    marshmallow.fields.Date: datetime.date,
    marshmallow.fields.DateTime: datetime.datetime,
    marshmallow.fields.Decimal: decimal.Decimal,
    marshmallow.fields.Dict: get_dict_type,
    marshmallow.fields.Email: pydantic.EmailStr,
    marshmallow.fields.Float: float,
    marshmallow.fields.Function: typing.Callable,
    marshmallow.fields.Int: int,
    marshmallow.fields.Integer: int,
    marshmallow.fields.List: get_list_type,
    marshmallow.fields.Mapping: typing.Mapping,
    marshmallow.fields.Method: typing.Callable,
    # marshmallow.fields.Nested: get_nested_model,
    marshmallow.fields.Number: typing.Union[pydantic.StrictFloat, pydantic.StrictInt],
    marshmallow.fields.Str: str,
    marshmallow.fields.String: str,
    marshmallow.fields.Time: datetime.time,
    marshmallow.fields.TimeDelta: datetime.timedelta,
    marshmallow.fields.URL: pydantic.AnyUrl,
    marshmallow.fields.Url: pydantic.AnyUrl,
    marshmallow.fields.UUID: str,
}


def is_custom_field(field):
    """If this is a subclass of marshmallow's Field and not in our list, we
    assume its a custom field"""
    ftype = type(field)
    if issubclass(ftype, marshmallow.fields.Field) and ftype not in FIELD_CONVERTERS:
        print("     Custom field")
        return True
    return False


def is_file_field(field):
    """If this is a file field, we need to handle it differently."""
    if field is not None and field.metadata.get("type") == "file":
        print("     File field")
        return True
    return False


def get_pydantic_type(field, optional=True):
    """Get pydantic type from a marshmallow field"""
    if field is None:
        return typing.Any
    elif is_file_field(field):
        conv = fastapi.UploadFile
    elif is_custom_field(field):
        conv = typing.Any
    else:
        conv = FIELD_CONVERTERS[type(field)]

    # Is there a cleaner way to check for annotation types?
    if isinstance(conv, type) or conv.__module__ == "typing":
        pyd_type = conv
    else:
        pyd_type = conv(field)

    if optional and not field.required:
        if is_file_field(field):
            # If we have a file field, do not wrap with Optional, as FastAPI does not
            # handle it correctly. Instead, we put None as default value later in the
            # outer function.
            pass
        else:
            pyd_type = typing.Optional[pyd_type]

    # FIXME(aloga): we need to handle enums
    return pyd_type


def sanitize_field_name(field_name):
    field_name = field_name.replace("-", "_")
    field_name = field_name.replace(" ", "_")
    field_name = field_name.replace(".", "_")
    field_name = field_name.replace(":", "_")
    field_name = field_name.replace("/", "_")
    field_name = field_name.replace("\\", "_")
    return field_name


def check_for_file_fields(fields):
    for _, field in fields.items():
        if is_file_field(field):
            return True
    return False


def pydantic_from_marshmallow(
    name: str, schema: marshmallow.Schema
) -> pydantic.BaseModel:
    """Convert a marshmallow schema to a pydantic model.

    May only work for fairly simple cases. Barely tested. Enjoy.
    """

    pyd_fields = {}
    have_file_fields = check_for_file_fields(schema._declared_fields)

    for field_name, field in schema._declared_fields.items():
        pyd_type = get_pydantic_type(field)

        description = field.metadata.get("description")

        if field.default:
            default = field.default
        elif field.missing:
            default = field.missing
        else:
            default = None

        if is_file_field(field):
            field_cls = fastapi.File
        elif have_file_fields:
            field_cls = fastapi.Form
        else:
            field_cls = pydantic.Field

        if field.required and not default:
            default = field_cls(
                ...,
                description=description,
                title=field_name,
                serialization_alias=field_name,
            )
        elif default is None:
            if is_file_field(field):
                # If we have a file field, it is not wraped with Optional, as FastAPI
                # does not handle it correctly (c.f. get_pydantic_type function above).
                # Instead, we put None as default value here, and FastAPI will handle it
                # correctly.
                default = None
            else:
                default = field_cls(
                    description=description,
                    title=field_name,
                    serialization_alias=field_name,
                )
        else:
            default = field_cls(
                description=description,
                default=default,
                title=field_name,
                serialization_alias=field_name,
            )

        field_name = sanitize_field_name(field_name)

        pyd_fields[field_name] = (pyd_type, default)

    ret = pydantic.create_model(
        name,
        **pyd_fields,
    )
    return ret


def get_pydantic_schema_from_marshmallow_fields(
    name: str,
    fields: dict,
) -> pydantic.BaseModel:

    model = marshmallow.Schema.from_dict(fields)

    pydantic_model = pydantic_from_marshmallow(name, model())

    return pydantic_model
