# -*- coding: utf-8 -*-

# Copyright Apache Software Foundation (ASF)
# Copyright 2018 Spanish National Research Council (CSIC)
#
# This code is based upon the openwhisk-runtime-docker reposiutory [1] from the
# Apache Software Foundation. Original copyright remains with the original
# authors
#
# [1]: https://github.com/apache/incubator-openwhisk-runtime-docker
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

import sys

from aiohttp import web
from oslo_config import cfg

from deepaas import api
from deepaas.openwhisk import handle

cli_opts = [
    cfg.StrOpt('base-openwhisk-path',
               default='/api/v1/web',
               help="""
Base path where OpenWhisk web actions are served.

This option is being used to build the base path for the swagger.json file
that is served as part of the OpenWhisk action. By default this configuration
variable points to "/api/v1/web/". We append to this variable the name of the
action, so that the swagger.json contains the correct basePath.
"""),
]

CONF = cfg.CONF
CONF.register_cli_opts(cli_opts)

LOG_SENTINEL = 'XXX_THE_END_OF_A_WHISK_ACTIVATION_XXX'

routes = web.RouteTableDef()

APP = None


# OpenWhisk calls the /init route when initializing the action, therefore we
# need this route. We use it as a singleton as we do not allow to reinit the
# action.
@routes.post('/init')
async def init(request):
    global APP

    try:
        message = await request.json()
    except Exception as e:
        return error_bad_request(msg="Error: {}".format(e))

    if message and not isinstance(message, dict):
        return error_bad_request()
    else:
        args = message.get('value', {}) if message else {}
        if not isinstance(args, dict):
            return error_bad_request()
        env = args.get('env', {})
        if not isinstance(env, dict):
            return error_bad_request()

    base = CONF.base_openwhisk_path
    action_name = env.get('__OW_ACTION_NAME', '')
    base_path = "{}{}".format(base, action_name)

    try:
        if APP is None:
            APP = await api.get_app(swagger=True,
                                    doc=False,
                                    base_path=base_path,
                                    enable_train=False)
        return web.Response(text="OK", status=200)
    except Exception as e:
        response = web.json_response(
            {'error': 'Internal error. {}'.format(e)},
            status=500
        )
        return complete(response)


# OpenWhisk will call the /run route when an action is invoked
@routes.get('/run')
@routes.post('/run')
async def run(request):
    if APP is None:
        response = web.json_response(
            {'error': 'The action is not intialized. See logs for details.'},
            status=502
        )
        return complete(response)

    req_clone = request.clone()
    try:
        message = await request.json()
    except Exception as e:
        return error_bad_request(msg="Error: {}".format(e))

    if message and not isinstance(message, dict):
        return error_bad_request()
    else:
        args = message.get('value', {}) if message else {}
        if not isinstance(args, dict):
            return error_bad_request()

    try:
        result = await handle.invoke(APP, req_clone, args)
        # NOTE(aloga): we got a response, even if it is a failure, therefore we
        # return a 200 error
        response = web.json_response(result, status=200)
    except Exception as e:
        # NOTE(aloga): something weird happened server-side, return a 500.
        response = web.json_response(
            {'error': 'Internal error. {}'.format(e)},
            status=500
        )
    return complete(response)


def error_bad_request(msg=None):
    if not msg:
        msg = 'The action did not receive a dictionary as an argument.'
    response = web.json_response({'error': msg}, status=400)
    return complete(response)


def complete(response):
    # Add sentinel to stdout/stderr
    sys.stdout.write('%s\n' % LOG_SENTINEL)
    sys.stdout.flush()
    sys.stderr.write('%s\n' % LOG_SENTINEL)
    sys.stderr.flush()
    return response


def main():
    proxy = web.Application(
        debug=CONF.debug,
        client_max_size=CONF.client_max_size,
    )
    proxy.initialized = False
    proxy.add_routes(routes)

    web.run_app(
        proxy,
        host=CONF.listen_ip,
        port=8080,
    )
