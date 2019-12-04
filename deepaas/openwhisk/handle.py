# -*- coding: utf-8 -*-

# Copyright Alex Milowski
# Copyright 2018 Spanish National Research Council (CSIC)
#
# This code is a fork of https://github.com/alexmilowski/flask-openwhisk with
# some modifications done here https://github.com/alvarolopez/flask-openwhisk
# and additional modifications done to work with aio-http
# Original copyright remains with the original author Alex Milowski
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

import base64
import re

from aiohttp import streams
from aiohttp import web
import aiohttp.web_urldispatcher
from werkzeug import http


block = set(['x-client-ip', 'x-forwarded-for',
             'x-forwarded-proto', 'x-global-transaction-id'])


def get_headers(headers):
    aux = {}
    for header in headers:
        if header not in block and not header.startswith('__ow'):
            aux[header] = str(headers[header])
    return aux


async def _check_request_resolves(request, path, app):
    alt_request = request.clone(rel_url=path)

    match_info = await app.router.resolve(alt_request)
    if not isinstance(match_info.route,
                      aiohttp.web_urldispatcher.SystemRoute):
        return True, match_info
    elif isinstance(match_info,
                    aiohttp.web_urldispatcher.MatchInfoError):
        if match_info.http_exception.status == 405:
            return True, match_info

    return False, match_info


async def _normalize(request, app):
    paths_to_check = []
    if '?' in request.raw_path:
        path, query = request.raw_path.split('?', 1)
        query = '?' + query
    else:
        query = ''
        path = request.raw_path

    paths_to_check.append(re.sub('//+', '/', path))
    paths_to_check.append(path + '/')
    paths_to_check.append(
        re.sub('//+', '/', path + '/'))

    for path in paths_to_check:
        resolves, match_info = await _check_request_resolves(
            request, path, app)
        if resolves:
            match_info.add_app(app)
            return match_info


async def invoke(app, request, args):
    headers = args.get('__ow_headers', {})
    method = args.get('__ow_method', 'GET').upper()
    path = args.get('__ow_path', '/')

    body = None
    if method in ('POST', 'PUT'):
        content_type = headers.get('content-type', 'application/octet-stream')
        parsed_content_type = http.parse_options_header(content_type)
        raw = args.get('__ow_body')
        if parsed_content_type[0][0:5] == 'text/':
            body = raw.encode(parsed_content_type[1].get('charset', 'utf-8'))
        else:
            body = base64.b64decode(raw) if raw is not None else None

    request = request.clone(
        method=method,
        rel_url=path,
        headers=get_headers(headers)
    )
    request._payload = streams.StreamReader(request._payload._protocol)
    request._payload.feed_data(body)
    request._payload.feed_eof()

    match_info = await _normalize(request, app)
    if match_info is None:
        response = web.HTTPNotFound()
    else:
        request._match_info = match_info
        try:
            if path == "/swagger.json":
                response = await match_info.handler(request)
            else:
                response = await match_info.handler(request, wsk_args=args)
        except web.HTTPException as e:
            response = e

    response_type = http.parse_options_header(
        response.headers.get('Content-Type', 'application/octet-stream'))

    if not response.body:
        body = None
    elif response_type[0][0:response_type[0].find('/')] != 'octet-stream':
        body = response.body.decode(response_type[1].get('charset', 'utf-8'))
    else:
        body = base64.b64encode(response.text)

    return {
        'headers': dict(response.headers),
        'statusCode': response.status,
        'body': body
    }
