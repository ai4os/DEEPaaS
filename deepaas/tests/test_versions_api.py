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


from aiohttp import web
import aiohttp_apispec
import pytest

from deepaas.api import v2
from deepaas.api import versions
from deepaas.tests import fake_responses


@pytest.fixture
async def application():
    app = web.Application()
    app.add_routes(versions.routes)

    app.add_subapp("/v2", v2.get_app())

    versions.Versions.versions = {}

    aiohttp_apispec.setup_aiohttp_apispec(
        app=app, url="/swagger.json", swagger_path="/api"
    )

    return app


async def test_get_no_versions(application, aiohttp_client):
    client = await aiohttp_client(application)
    ret = await client.get("/")
    assert 200 == ret.status
    assert fake_responses.empty_versions == await ret.json()


async def test_v2_version(application, aiohttp_client):
    versions.register_version("stable", v2.get_version)
    client = await aiohttp_client(application)
    ret = await client.get("/")
    assert 200 == ret.status
    assert fake_responses.versions == await ret.json()
