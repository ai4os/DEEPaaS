#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2020 Spanish National Research Council (CSIC)
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

import collections
import mimetypes
import os
import shutil
import sys


from oslo_config import cfg
from oslo_log import log

from deepaas.model import loading

cli_opts = [
    cfg.StrOpt('input_file',
               short="i",
               required=True,
               help="""
Set local input file to predict.
"""),
    cfg.StrOpt('content_type',
               default='application/json',
               short='ct',
               help="""
Especify the content type of the output file. The available options are
(image/png, application/json (by default), application/zip).
"""),
    cfg.StrOpt('output',
               short="o",
               required=True,
               help="""
Save the result to a local file.
"""),
    cfg.BoolOpt('url',
                short='u',
                default=False,
                help="""
Run as input file an URL.
If this option is set to True, we can use the URL
of an image as an input file.
"""),
]

CONF = cfg.CONF
CONF.register_cli_opts(cli_opts)

LOG = log.getLogger(__name__)

# Loading the model installed


def model_name():
    global MODEL_NAME
    try:
        for name, model in loading.get_available_models("v2").items():
            MODEL_NAME = name
    except Exception as e:
        LOG.warning("Error loading models: %s", e)


def prediction(input_file, file_type, content_type):
    model_name()  # Function to know the name of the installed model

    package_name = MODEL_NAME
    predict_data = __import__(package_name).api.predict_data  # Import function
    predict_url = __import__(package_name).api.predict_url  # Import function

    UploadedFile = collections.namedtuple("UploadedFile", ("name",
                                                           "filename",
                                                           "content_type"))

    file = UploadedFile(name=input_file,
                        filename=input_file,
                        content_type='image/png')

    if file_type is True:
        input_data = {'urls': [input_file], 'accept': content_type}
        output_pred = predict_url(input_data)
    else:
        input_data = {'files': [file], 'accept': content_type}
        output_pred = predict_data(input_data)

    return (output_pred)


def main():
    cfg.CONF(sys.argv[1:])
    input_file = CONF.input_file
    content_type = CONF.content_type
    file_type = CONF.url
    output = CONF.output

    output_pred = prediction(input_file, file_type, content_type)
    print(output_pred)
    extension = mimetypes.guess_extension(content_type)
    out_file_name = "out_" + os.path.splitext(os.path.basename(input_file))[0]
    if extension is None:
        sys.stderr.write(
            "ERROR: Content type {} not valid.\n".format(content_type))
        sys.exit(1)
    if extension == ".json":
        f = open(out_file_name + ".json", "w+")
        f.write(repr(output_pred) + '\n')
        f.close()
        if not os.path.exists(output):  # Create path if does not exist
            os.makedirs(output)
        dir_name = output + f.name
        shutil.move(f.name, os.path.join(output, f.name))

    if extension == '.png':
        output_path_image = output_pred.name  # Path of resulting image
        print(output_pred)
        dir_name = output + out_file_name
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)   # Remove path if exist
        shutil.copytree(os.path.dirname(output_path_image), dir_name)

    if extension == '.zip':
        print(output_pred)
        dir_name = output + out_file_name + ".zip"
        if not os.path.exists(output):  # Create path if does not exist
            os.makedirs(output)
        shutil.move(output_pred.name, dir_name)

    print("Output saved at {}" .format(dir_name))


if __name__ == "__main__":
    main()