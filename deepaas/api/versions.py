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

import flask
import flask_restplus
from flask_restplus import fields
import werkzeug.routing

import deepaas

ns = flask_restplus.Namespace(
    '',
    description='API Version information.')


def get_blueprint(doc="/", add_specs=True):
    bp = flask.Blueprint('versions', __name__)

    api = flask_restplus.Api(
        bp,
        title='DEEP as a Service API version information',
        version=deepaas.__version__,
        description='DEEP as a Service (API) version information endpoint',
        doc=doc,
        add_specs=add_specs,
    )
    api.add_namespace(ns)

    return bp


version_link = ns.model('Location', {
    "rel": fields.String(required=True),
    "href": fields.Url(required=True)
})

api_version = ns.model('Version', {
    "version": fields.String(required="True"),
    "link": fields.Nested(version_link)
})

versions = ns.model('Versions', {
    'versions': fields.List(fields.Nested(api_version)),
})


@ns.marshal_with(versions, envelope='versions')
@ns.route('/')
class Versions(flask_restplus.Resource, object):

    versions = {}

    @classmethod
    def register_version(cls, version, url):
        cls.versions[version] = url

    def get(self):
        """Return available API versions."""
        versions = []
        for k, v in self.versions.items():
            versions.append({
                "version": k,
                "links": [
                    {
                        "rel": "self",
                        "href": flask.url_for(v),
                    },
                ]
            })

            try:
                doc = "%s.doc" % v.split(".")[0]
                d = {"rel": "help",
                     "href": flask.url_for(doc)}
            except werkzeug.routing.BuildError:
                pass
            else:
                versions[-1]["links"].append(d)

            try:
                specs = "%s.specs" % v.split(".")[0]
                d = {"rel": "describedby",
                     "href": flask.url_for(specs)}
            except werkzeug.routing.BuildError:
                pass
            else:
                versions[-1]["links"].append(d)

        return {"versions": versions}


def register_version(version, url):
    # NOTE(aloga): we could use a @classmethod on Versions, but it fails
    # with a TypeError: 'classmethod' object is not callable since the function
    # is decorated.
    Versions.versions[version] = url
