#!/usr/bin/env python -*- coding: utf-8 -*-

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

import mimetypes
import os
import shutil
import sys

from oslo_config import cfg
from oslo_log import log

from deepaas.model import loading
from deepaas.model.v2.wrapper import UploadedFile

cli_opts = [
    cfg.StrOpt('model-name',
               help="""
Add the name of the model from which you want
to obtain the prediction.
If there are multiple models installed and youd don't
specify the name of the one you want to use the program will fail.
If there is only one model installed, that will be used
to make the prediction.
"""),
    cfg.StrOpt('input-file',
               short="i",
               help="""
Set local input file to predict.
"""),
    cfg.StrOpt('content-type',
               default='application/json',
               short='ct',
               help="""
Especify the content type of the output file. The selected
option must be available in the model used.
(by default application/json).
"""),
    cfg.StrOpt('output',
               short="o",
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


def get_model_name():
    model_name = CONF.model_name
    models = loading.get_available_models("v2")
    if model_name:
        model_obj = models.get(model_name)
        if model_obj is None:
            sys.stderr.write(
                "ERROR: The model {} is not available.\n".format(model_name))
            sys.exit(1)
        return model_name, model_obj
    elif len(models) == 1:
        return models.popitem()
    else:
        sys.stderr.write(
            'ERROR: There are several models available ({}) '
            'you have to choose one.\n'.format(list(models.keys())))
        sys.exit(1)


def prediction(input_file, file_type, content_type):

    model_name, model_obj = get_model_name()
    predict_data = model_obj.predict_data
    predict_url = model_obj.predict_url

    if file_type is True:
        input_data = {'urls': [input_file], 'accept': content_type}
        output_pred = predict_url(input_data)
    else:
        content_type_in, fileEncoding = mimetypes.guess_type(input_file)
        file = UploadedFile(name=input_file,
                            filename=input_file,
                            content_type=content_type_in)
        input_data = {'files': [file], 'accept': content_type}
        output_pred = predict_data(input_data)

    return (output_pred)


def main():
    cfg.CONF(sys.argv[1:])
    input_file = CONF.input_file
    content_type = CONF.content_type
    file_type = CONF.url
    output = CONF.output

    # Checking required argument
    if input_file is None:
        sys.stderr.write(
            "ERROR: Option input_file is required.\n")
        sys.exit(1)

    if output is None:
        sys.stderr.write(
            "ERROR: Option output is required.\n")
        sys.exit(1)

    output_pred = prediction(input_file, file_type, content_type)
    extension = mimetypes.guess_extension(content_type)
    if extension is None or output_pred is None:
        sys.stderr.write(
            "ERROR: Content type {} not valid.\n".format(content_type))
        sys.exit(1)
    if extension == ".json":
        name_image = os.path.splitext(os.path.basename(input_file))[0]
        out_file_name = "out_" + name_image
        f = open(out_file_name + ".json", "w+")
        f.write(repr(output_pred) + '\n')
        f.close()
        if not os.path.exists(output):  # Create path if does not exist
            os.makedirs(output)
        dir_name = output + f.name
        shutil.move(f.name, os.path.join(output, f.name))
    else:
        output_path_image = output_pred.name
        dir_name = output + os.path.basename(output_path_image)
        if not os.path.exists(output):  # Create path if does not exist
            os.makedirs(output)
        shutil.copy(output_path_image, output)

    print("Output saved at {}" .format(dir_name))


if __name__ == "__main__":
    main()
