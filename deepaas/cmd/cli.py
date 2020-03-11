#!/usr/bin/env python -*- coding: utf-8 -*-

# Copyright 2020 Spanish National Research Council (CSIC)
# Copyright (c) 2018 - 2020 Karlsruhe Institute of Technology - SCC
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


import argparse
import json
import mimetypes
import os
import re
import shutil
import sys
import tempfile
import time

from oslo_log import log

from deepaas.model import loading
from deepaas.model.v2.wrapper import UploadedFile

LOG = log.getLogger(__name__)

debug_cli = False


# Convert mashmallow fields to dict()
def _fields_to_dict(fields_in):
    """Function to convert mashmallow fields to dict()"""

    dict_out = {}

    for key, val in fields_in.items():
        param = {}
        param['default'] = val.missing
        param['type'] = type(val.missing)
        if key == 'files' or key == 'urls':
            param['type'] = str

        val_help = val.metadata['description']
        # argparse hates % sign:
        if '%' in val_help:
            # replace single occurancies of '%' with '%%'
            # since '%%' is accepted by argparse
            val_help = re.sub(r'(?<!%)%(?!%)', r'%%', val_help)

        if 'enum' in val.metadata.keys():
            val_help = "{}. Choices: {}".format(val_help,
                                                val.metadata['enum'])
        param['help'] = val_help

        try:
            val_req = val.required
        except Exception:
            val_req = False
        param['required'] = val_req

        dict_out[key] = param
    return dict_out


# Loading a model
def _get_model_name(model_name=None):
    """Function to get model_obj from the name of the model.
    In case of error, prints the list of available models
    """

    models = loading.get_available_models("v2")
    if model_name:
        model_obj = models.get(model_name)
        if model_obj is None:
            sys.stderr.write(
                "[ERROR]: The model {} is not available.\n"
                "Available models: {}\n".format(model_name,
                                                list(models.keys())))
            sys.exit(1)
        return model_name, model_obj
    elif len(models) == 1:
        return models.popitem()
    else:
        sys.stderr.write(
            '[ERROR]: There are several models available ({}).\n'
            'You have to choose one and set it in the DEEPAAS_V2_MODEL '
            'environment setting.\n'.format(list(models.keys())))
        sys.exit(1)


# DEFINE ARGS with ARGPARSE
# By default assume a single loaded model.
# If many available, one has to provide which one to load
# via DEEPAAS_V2_MODEL environment setting
model_name = None
if 'DEEPAAS_V2_MODEL' in os.environ:
    model_name = os.environ['DEEPAAS_V2_MODEL']

model_name, model_obj = _get_model_name(model_name)

parser = argparse.ArgumentParser(description='Model parameters',
                                 add_help=False)

# intentionally long to avoid conflict with flags from predict, train etc
parser.add_argument('--deepaas_model_output',
                    help="Define an output file, if needed")

cmd_parser = argparse.ArgumentParser()
subparsers = cmd_parser.add_subparsers(help='Use \"{} method --help\" to get'
                                       'more info on options for'
                                       'each method'.format(parser.prog),
                                       dest='method')

get_metadata_parser = subparsers.add_parser('get_metadata',
                                            help='get_metadata method',
                                            parents=[parser])

get_warm_parser = subparsers.add_parser('warm',
                                        help='warm method, e.g. to prepare'
                                        'the model for execution',
                                        parents=[parser])

# get train arguments configured
train_parser = subparsers.add_parser('train',
                                     help='commands for training',
                                     parents=[parser])

train_args = _fields_to_dict(model_obj.get_train_args())
for key, val in train_args.items():
    train_parser.add_argument('--%s' % key,
                              default=val['default'],
                              type=val['type'],
                              help=val['help'],
                              required=val['required'])

# get predict arguments configured
predict_parser = subparsers.add_parser('predict',
                                       help='commands for prediction',
                                       parents=[parser])

predict_args = _fields_to_dict(model_obj.get_predict_args())
for key, val in predict_args.items():
    predict_parser.add_argument('--%s' % key,
                                default=val['default'],
                                type=val['type'],
                                help=val['help'],
                                required=val['required'])

args = cmd_parser.parse_args()
# FINISH with ARGS


# store DEEPAAS_MODEL output in a file
def _store_output(results, out_file):
    """Function to store model results in the file
    :param results:  what to store (JSON expected)
    :param out_file: in what file to store
    """

    out_path = os.path.dirname(os.path.abspath(out_file))
    if not os.path.exists(out_path):  # Create path if does not exist
        os.makedirs(out_path)

    f = open(out_file, "w+")
    f.write(results)
    f.close()
    print("[OUTPUT] Output is saved in {}".format(out_file))


def main():
    """Executes model's methods with corresponding parameters"""

    # TODO(multi-file): change to many files ('for' itteration)
    if args.__contains__('files'):
        if args.files:
            # create tmp file as later it supposed
            # to be deleted by the application
            temp = tempfile.NamedTemporaryFile()
            temp.close()
            # copy original file into tmp file
            with open(args.files, "rb") as f:
                with open(temp.name, "wb") as f_tmp:
                    for line in f:
                        f_tmp.write(line)

            # create file object
            file_type = mimetypes.MimeTypes().guess_type(args.files)[0]
            file_obj = UploadedFile(name="data",
                                    filename=temp.name,
                                    content_type=file_type,
                                    original_filename=args.files)
            args.files = file_obj

    if args.method == 'get_metadata':
        meta = model_obj.get_metadata()
        meta_json = json.dumps(meta)
        print("[OUTPUT]:\n{}".format(meta_json)) if debug_cli else ''
        if args.deepaas_model_output:
            _store_output(meta_json, args.deepaas_model_output)

        return meta_json
    elif args.method == 'warm':
        model_obj.warm()
        print("[INFO] Finished warm()")
    elif args.method == 'predict':
        # call predict method
        results = model_obj.predict(**vars(args))

        if args.deepaas_model_output:
            out_file = args.deepaas_model_output
            out_path = os.path.dirname(os.path.abspath(out_file))
            if not os.path.exists(out_path):  # Create path if does not exist
                os.makedirs(out_path)
            # check extension of the output file
            out_filename, out_extension = os.path.splitext(out_file)

            # set default extension for the data returned
            # by the application to .json
            extension = ".json"
            # check what is asked to return by the application (if --accept)
            if args.__contains__('accept'):
                if args.accept:
                    extension = mimetypes.guess_extension(args.accept)

            if (extension is not None and out_extension is not None
                    and extension != out_extension):
                out_file = out_file + extension
                print("[WARNING] You are trying to store {} "
                      "type data in the file "
                      "with {} extension!\n"
                      "......... New output is {}".format(extension,
                                                          out_extension,
                                                          out_file))
            if extension == ".json" or extension is None:
                results_json = json.dumps(results)
                if debug_cli:
                    print("[OUTPUT]:\n{}".format(results_json))
                f = open(out_file, "w+")
                f.write(results_json)
                f.close()
            else:
                out_results = results.name
                shutil.copy(out_results, out_file)

            print("[OUTPUT] Output is saved in {}" .format(out_file))

        return results
    elif args.method == 'train':
        start = time.time()
        results = model_obj.train(**vars(args))
        print("Elapsed time:  ", time.time() - start)
        # we assume that train always returns JSON
        results_json = json.dumps(results)
        if debug_cli:
            print("[OUTPUT]:\n{}".format(results_json))
        if args.deepaas_model_output:
            _store_output(results_json, args.deepaas_model_output)

        return results_json


if __name__ == '__main__':
    main()
