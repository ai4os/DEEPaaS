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
import inspect
import json
import keyword
import typing

import fastapi
import fastapi.encoders
import fastapi.exceptions
import marshmallow
import marshmallow.fields
import marshmallow.validate
import pydantic


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
        return True
    return False


def is_file_field(field):
    """If this is a file field, we need to handle it differently."""
    if field is not None and field.metadata.get("type") == "file":
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
        # Keep the format (e.g. "password"), as clients use it to render values
        extra = None
        if field.metadata.get("format"):
            extra = {"format": field.metadata["format"]}

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
                json_schema_extra=extra,
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
                    json_schema_extra=extra,
                    title=field_name,
                    serialization_alias=field_name,
                )
        else:
            default = field_cls(
                description=description,
                default=default,
                json_schema_extra=extra,
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


def _get_field_description(field):
    return field.metadata.get("description")


def _get_field_openapi_schema(field):
    """Get the OpenAPI schema of a (non file) marshmallow field."""
    try:
        pyd_type = get_pydantic_type(field, optional=False)
        schema = pydantic.TypeAdapter(pyd_type).json_schema()
    except Exception:
        schema = {}

    default = field.load_default
    if default is not marshmallow.missing and not callable(default):
        schema["default"] = fastapi.encoders.jsonable_encoder(default)

    validators = field.validators or []
    for v in validators:
        if isinstance(v, marshmallow.validate.OneOf):
            schema["enum"] = list(v.choices)
        elif isinstance(v, marshmallow.validate.Range):
            if v.min is not None:
                schema["minimum"] = v.min
            if v.max is not None:
                schema["maximum"] = v.max
    if "enum" not in schema and field.metadata.get("enum"):
        schema["enum"] = list(field.metadata["enum"])
    if field.metadata.get("format"):
        schema["format"] = field.metadata["format"]

    return schema


def _get_openapi_parameters(fields):
    """Document the (non file) arguments as query parameters, as in v2."""
    params = []
    for name, field in fields.items():
        param = {
            "name": name,
            "in": "query",
            "required": bool(field.required),
            "schema": _get_field_openapi_schema(field),
        }
        description = _get_field_description(field)
        if description:
            param["description"] = description
        params.append(param)
    return params


def _get_raw_value(field, sources):
    """Get the raw value of a field from the first source that contains it.

    :param sources: list of multi-dict like objects (query, form) or dicts
        (JSON body), in order of precedence.
    """
    key = field.data_key or field.name
    is_list = isinstance(field, marshmallow.fields.List)
    for source in sources:
        if key not in source:
            continue
        if is_list and hasattr(source, "getlist"):
            values = source.getlist(key)
            # Allow sending lists as a single JSON encoded value
            if len(values) == 1 and isinstance(values[0], str):
                try:
                    decoded = json.loads(values[0])
                except ValueError:
                    pass
                else:
                    if isinstance(decoded, list):
                        values = decoded
            return values
        value = source[key]
        if isinstance(field, marshmallow.fields.Dict) and isinstance(value, str):
            try:
                value = json.loads(value)
            except ValueError:
                pass
        return value
    return marshmallow.missing


async def _get_request_sources(request):
    """Get the request query string, form and JSON body, if any."""
    sources = [request.query_params]
    content_type = request.headers.get("content-type", "")
    if content_type.startswith(
        ("multipart/form-data", "application/x-www-form-urlencoded")
    ):
        form = await request.form()
        sources.append(form)
    elif content_type.startswith("application/json"):
        try:
            body = await request.json()
        except ValueError:
            body = None
        if isinstance(body, dict):
            sources.append(body)
    return sources


def _validation_error(error):
    """Convert a marshmallow error to a FastAPI request validation error."""
    errors = []
    for name, messages in error.normalized_messages().items():
        if isinstance(messages, dict):
            messages = [f"{k}: {v}" for k, v in messages.items()]
        elif not isinstance(messages, (list, tuple)):
            messages = [messages]
        errors.append(
            {
                "type": "value_error",
                "loc": ("query", name),
                "msg": " ".join(str(m) for m in messages),
                "input": None,
            }
        )
    return fastapi.exceptions.RequestValidationError(errors)


def get_arguments_parser(fields: dict):
    """Get a FastAPI dependency that parses the arguments declared by a model.

    As in DEEPaaS v2, the arguments are deserialized and validated using the
    marshmallow fields declared by the model, so that types, defaults and
    validators (e.g. ``Range`` or ``OneOf``) behave exactly as before.
    Arguments can be sent in the query string, as form fields or in a JSON
    body (looked up in that order), and keep their original names. Files are
    handled by FastAPI as multipart uploads.

    :param fields: dictionary of marshmallow fields, as returned by the
        model's ``get_predict_args``.
    :returns: a tuple with the dependency (returning a dictionary with the
        parsed arguments) and the OpenAPI definition of the parameters.
    """
    file_fields = {}
    other_fields = {}
    for name, field in fields.items():
        if is_file_field(field):
            file_fields[name] = field
        else:
            other_fields[name] = field

    schema = marshmallow.Schema.from_dict(other_fields)(unknown=marshmallow.EXCLUDE)

    params = [
        inspect.Parameter(
            "request",
            inspect.Parameter.KEYWORD_ONLY,
            annotation=fastapi.Request,
        )
    ]
    file_names = {}
    for name, field in file_fields.items():
        # NOTE(aloga): FastAPI documents the multipart fields with the name of
        # the parameter (not with its alias), so use the argument name if it
        # is a valid identifier, so that clients built from the OpenAPI spec
        # (e.g. Swagger UI) send the files with the right name.
        if name.isidentifier() and not keyword.iskeyword(name) and name != "request":
            param_name = name
        else:
            param_name = f"file_{len(file_names)}"
        file_names[param_name] = name
        description = _get_field_description(field)
        if field.required:
            annotation = fastapi.UploadFile
            default = fastapi.File(..., alias=name, description=description)
        else:
            annotation = typing.Optional[fastapi.UploadFile]
            default = fastapi.File(None, alias=name, description=description)
        params.append(
            inspect.Parameter(
                param_name,
                inspect.Parameter.KEYWORD_ONLY,
                annotation=annotation,
                default=default,
            )
        )

    async def parse_arguments(request, **files):
        sources = await _get_request_sources(request)
        data = {}
        for field in schema.fields.values():
            value = _get_raw_value(field, sources)
            if value is not marshmallow.missing:
                data[field.data_key or field.name] = value
        try:
            args = schema.load(data)
        except marshmallow.ValidationError as e:
            raise _validation_error(e)

        for param_name, name in file_names.items():
            args[name] = files.get(param_name)
        return args

    parse_arguments.__signature__ = inspect.Signature(params)

    return parse_arguments, _get_openapi_parameters(other_fields)
