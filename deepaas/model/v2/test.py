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

import time

from oslo_log import log
from webargs import fields
from webargs import validate

from deepaas.model.v2 import base

LOG = log.getLogger(__name__)


class TestModel(base.BaseModel):
    """Dummy model implementing minimal functionality.

    This is a simple class that mimics the behaviour of a module, just for
    showing how the whole DEEPaaS works and documentation purposes.
    """

    name = "deepaas-test"

    # FIXME(aloga): document this
    schema = {
        "date": fields.Date(),
        "labels": fields.List(
            fields.Nested(
                {
                    "label": fields.Str(),
                    "probability": fields.Float(),
                },
            )
        ),
    }

    _logo = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x1e\x00\x00\x00"
        b"\r\x08\x04\x00\x00\x00\x14{\x16\x1c\x00\x00\x02\x13IDAT(\xcf\x8d"
        b"\xd2?h\x94w\x00\xc6\xf1\xcf\xef\xbd\xfc9\xe3\x19\xacb\x8c\xa2C"
        b"\x13-\x81\xe8 (\x11\xa4\x831 \xb4v\xb0B\xc0B\xa5\x10\x1c\x1c\xc4"
        b"\xd2RQ\x14T\xecRE\xcd\xd0\x16\x11$\x8a\x82E\xba(\xddl\xc1:J\xa8CC"
        b"\xd2\x98\xd8\xd2\x10EI\xcc\xdd\xe9\xdd\xbdw^\xee=\x07\x15\x17"
        b"\x07\xbf\xd33<\xdf\xe1\x81\x87\xb7l\x95\xd5\xf6*\xb6\t\xcd\xb6"
        b"\x19\xb0!\x8a\xbc\x17[\xe5\xde\xc8\x9a]7\xaf\xa8l\x7f\xca\xb7"
        b"\xf6\xbdSh\xa0\xd7\x9d0\x9f\x8e*\tX,\xb7F\x8f5v\xfa\xdaM\x07u"
        b"\xd5>>\xb3E\xc5\xad\xcc\xc8G\x9ez\x18\xe6;\xb4\x9b\xecx\xf2\x1f!"
        b"\xd2o\xd8\xac\x11Cr\xda}\xe3\xb9X\xcds+\xd3B\xb3S\xca\xe6<S"
        b"\xf4\x9d\xd5\xae\xb9\xa9$\x96u44\xb2[\xc9y\xfdN+\xc9\xfbB\xc5e;"
        b"\xcc\xb9gQ\x94\xf2\xbd\xaa\x1f,u\\\xa2l@\xc5#\xbbu;\xach/\xe3~"
        b"\nQ\x9f\xa6\xe0\xa8\xbc?<\xd0m\xd4\x84\xce\x86\xe0\x88\x17NE\x8d"
        b"\xbeRv\xd1S\xbf\x89\xf5\x0f \n\xce\x19\xa7f\xd7\xeb\xfd\xbd\xf2"
        b"\xc6\x0c\x1b6e}\x149\xa0\xe2\xe7\xd0d\x97\x82+ZM\xb9\xadh\xed"
        b"\xeb\xf6\xe7\xaaL\x1a\x8c\xa2Ni\x0e\xc9\xb9\xa2n\xc6\xa6\x86`@"
        b"\xc5\xa5\xd0\xa4O\xde\x8d\xd0\xa2\xcf\x0bg\xc5\xb6\x7f\x824\xc7L"
        b"\xb1G\xd1\xa0\xcf\x9cT\x90\xb7\xd1\xbf\xb2\x86\xfc\xa2\xec\xba"
        b"\x16\xc1\xaf\x12W\r\x9auO\x8f\x8a1=\x96\xe8\x97uXH\xf9\xd2\xdfr"
        b"\xee\xbb\xe0\xae\xa5:\x9c7f\xd4\t\x0b\xdb\xf4\xb2\xdc\x8f\xfe7m"
        b"\xc8j]b\xa3b9%\x17\xb5\x04\xed\x92\xf0\xac\xbeB!\xca'\x8b\xc5"
        b"\xd2\x16\xc9\x84I\xea\x0b\x94\xb4j\x93\x0b9\xd5\xa8Z\xcbX\xe7"
        b"\x96MVXe$\xf5W\x924\xd8\xac\xb5\xfe\xd02IRU\x901%\xa3P\xef\xf5"
        b"\x81'>4\x1b\xddH>\xad7*\xd7\xb2V\n\xa8\xf8\x1djH)z\xa0\xd30\xfe1#"
        b"\x98V\xd5d\xce\x8c\xa2\x92\x89\xfa*\xd3xl^lZ\xde\x9f\xe27\xf7|"
        b"\tz\x97\xc9?\xa6\x13[\xb9\x00\x00\x00\x00IEND\xaeB`\x82"
    )

    def warm(self):
        LOG.debug("Test model is warming...")

    def predict(self, **kwargs):
        LOG.debug("Got the following kw arguments: %s", kwargs)
        d = {
            "date": "2019-01-1",
            "labels": [{"label": "foo", "probability": 1.0}]
        }
        if kwargs.get("accept") == "text/plain":
            return str(d)
        elif kwargs.get("accept") == "image/png":
            return self._logo
        return d

    def train(self, *args, **kwargs):
        sleep = kwargs.get("sleep", 1)
        LOG.debug("Got the following arguments: %s", args)
        LOG.debug("Got the following kw arguments: %s", kwargs)
        LOG.debug("Starting training, ending in %is" % sleep)
        time.sleep(sleep)

    def get_predict_args(self):
        return {
            "data": fields.Field(
                description="Data file to perform inference.",
                required=True,
                location="form",
                type="file",
            ),
            "parameter": fields.Int(
                description="This is a parameter for prediction",
                required=True
            ),
            "parameter_three": fields.Str(
                description=("This is a parameter that forces its value to "
                             "be one of the choices declared in 'enum'"),
                enum=["foo", "bar"],
                validate=validate.OneOf(["foo", "bar"]),
            ),
            "accept": fields.Str(
                description=("Media type(s) that is/are acceptable for the "
                             "response."),
                validate=validate.OneOf(["text/plain", "image/png"]),
                location="headers",
            )
        }

    def get_train_args(self):
        return {
            "sleep": fields.Int(
                required=True,
                descripton='This is a integer parameter, and it is '
                           'a required one.'
            ),
            "parameter_two": fields.Str(
                description='This is a string parameter.'
            ),
        }

    def get_metadata(self):
        d = {
            "id": "0",
            "name": "deepaas-test",
            "description": ("This is not a model at all, just a placeholder "
                            "for testing the API functionality. If you are "
                            "seeing this, it is because DEEPaaS could not "
                            "load a valid model."),
            "author": "Alvaro Lopez Garcia",
            "version": "0.0.1",
            "url": "https://github.com/indigo-dc/DEEPaaS/",
            "license": "Apache 2.0",
        }
        return d
