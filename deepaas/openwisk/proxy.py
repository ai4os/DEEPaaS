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

import flask
from gevent import wsgi
from oslo_config import cfg

from deepaas import api
from deepaas.openwisk import handle

CONF = cfg.CONF

LOG_SENTINEL = 'XXX_THE_END_OF_A_WHISK_ACTIVATION_XXX'

proxy = flask.Flask(__name__)
proxy.debug = False
proxy.initialized = False

APP = None


# OpenWhisk calls the /init route when initializing the action, therefore we
# need this route. We use it as a singleton as we do not allow to reinit the
# action.
@proxy.route('/init', methods=['POST'])
def init():
    global APP

    try:
        if APP is None:
            APP = api.get_app(doc=False)
        return ('OK', 200)
    except Exception as e:
        response = flask.jsonify({'error': 'Internal error. {}'.format(e)})
        response.status_code = 500
        return complete(response)


# OpenWhisk will call the /run route when an action is invoked
@proxy.route('/run', methods=['POST', "GET"])
def run():
    message = flask.request.get_json(force=True, silent=True)
    if message and not isinstance(message, dict):
        return error_bad_request()
    else:
        args = message.get('value', {}) if message else {}
        if not isinstance(args, dict):
            return error_bad_request()

    if APP is not None:
        try:
            result = handle.invoke(APP, args)
            response = flask.jsonify(result)
            response.status_code = 200
        except Exception as e:
            response = flask.jsonify({'error': 'Internal error. {}'.format(e)})
            response.status_code = 500
    else:
        response = flask.jsonify({'error': 'The action is not intialized. '
                                           'See logs for details.'})
        response.status_code = 502
    return complete(response)


def error_bad_request():
    response = flask.jsonify({'error': 'The action did not receive a '
                              'dictionary as an argument.'})
    response.status_code = 400
    return complete(response)


def complete(response):
    # Add sentinel to stdout/stderr
    sys.stdout.write('%s\n' % LOG_SENTINEL)
    sys.stdout.flush()
    sys.stderr.write('%s\n' % LOG_SENTINEL)
    sys.stderr.flush()
    return response


def main():
    server = wsgi.WSGIServer((CONF.listen_ip, 8080), proxy, log=None)
    server.serve_forever()
