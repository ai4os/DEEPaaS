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


# import asyncio
import deepaas
import json
import mimetypes
import multiprocessing as mp
import os
import re
import shutil
import sys
import tempfile
import time

from oslo_config import cfg
from oslo_log import log

# from deepaas import config
from deepaas.model import loading
from deepaas.model.v2 import wrapper as v2_wrapper


debug_cli = False


# Helper function to get subdictionary from dict_one based on keys in dict_two
def _get_subdict(dict_one, dict_two):
    """Function to get subdictionary from dict_one based on keys in dict_two
    :param dict_one: dict to select subdictionary from
    :param dict_two: dict, its keys are used to select entries from dict_one
    :return: selected subdictionary
    """
    sub_dict = {k: dict_one[k] for k in dict_two.keys() if k in dict_one}
    return sub_dict


# Convert mashmallow fields to dict()
def _fields_to_dict(fields_in):
    """Function to convert mashmallow fields to dict()
    :param fields_in: mashmallow fields
    :return: python dictionary
    """

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


# Function to get a model object
def _get_model_name(model_name=None):
    """Function to get model_obj from the name of the model.
    In case of error, prints the list of available models
    :param model_name: name of the model
    :return: model object
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


# Get the model name
model_name = None
if 'DEEPAAS_V2_MODEL' in os.environ:
    model_name = os.environ['DEEPAAS_V2_MODEL']

model_name, model_obj = _get_model_name(model_name)

# use deepaas.model.v2.wrapper.ModelWrapper(). deepaas>1.2.1dev4
# model_obj = v2_wrapper.ModelWrapper(name=model_name,
#                                    model_obj=model_obj)


# Once we know the model name,
# we get arguments for predict and train as dictionaries
predict_args = _fields_to_dict(model_obj.get_predict_args())
train_args = _fields_to_dict(model_obj.get_train_args())


# Function to add later these arguments to CONF via SubCommandOpt
def _add_methods(subparsers):
    """Function to add argparse subparsers via SubCommandOpt (see below)
    for DEEPaaS methods get_metadata, warm, predict, train
    """

    # in case no method requested, we return get_metadata(). check main()
    subparsers.required = False

    get_metadata_parser = subparsers.add_parser('get_metadata',  # noqa: F841
                                                help='get_metadata method')

    get_warm_parser = subparsers.add_parser('warm',              # noqa: F841
                                            help='warm method, e.g. to '
                                            'prepare the model for execution')

    # get predict arguments configured
    predict_parser = subparsers.add_parser('predict',
                                           help='predict method, use '
                                           'predict --help for the full list')

    for key, val in predict_args.items():
        predict_parser.add_argument('--%s' % key,
                                    default=val['default'],
                                    type=val['type'],
                                    help=val['help'],
                                    required=val['required'])
    # get train arguments configured
    train_parser = subparsers.add_parser('train',
                                         help='train method, use '
                                         'train --help for the full list')

    for key, val in train_args.items():
        train_parser.add_argument('--%s' % key,
                                  default=val['default'],
                                  type=val['type'],
                                  help=val['help'],
                                  required=val['required'])


# Now options to be registered with oslo_config
cli_opts = [
    # intentionally long to avoid a conflict with opts from predict, train etc
    cfg.StrOpt('deepaas_method_output',
               help="Define an output file, if needed",
               deprecated_name='deepaas_model_output'),
    cfg.BoolOpt('deepaas_with_multiprocessing',
                default=True,
                help='Activate multiprocessing; default is True'),
    cfg.SubCommandOpt('methods',
                      title='methods',
                      handler=_add_methods,
                      help='Use \"<method> --help\" to get '
                      'more info about options for '
                      'each method')
]


CONF = cfg.CONF
CONF.register_cli_opts(cli_opts)

LOG = log.getLogger(__name__)


# store DEEPAAS_METHOD output in a file
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

    LOG.info("[INFO, Output] Output is saved in {}".format(out_file))


# async def main():
def main():
    """Executes model's methods with corresponding parameters"""

    # we may add deepaas config, but then too many options...
    # config.config_and_logging(sys.argv)

    log.register_options(CONF)
    log.set_defaults(default_log_levels=log.get_default_log_levels())

    CONF(sys.argv[1:],
         project='deepaas',
         version=deepaas.__version__)

    log.setup(CONF, "deepaas-cli")

    LOG.info("[INFO, Method] {} was called.".format(CONF.methods.name))

    # put all variables in dict, makes life easier...
    conf_vars = vars(CONF._namespace)

    if CONF.deepaas_with_multiprocessing:
        mp.set_start_method('spawn', force=True)

    # TODO(multi-file): change to many files ('for' itteration)
    if CONF.methods.__contains__('files'):
        if CONF.methods.files:
            # create tmp file as later it supposed
            # to be deleted by the application
            temp = tempfile.NamedTemporaryFile()
            temp.close()
            # copy original file into tmp file
            with open(conf_vars['files'], "rb") as f:
                with open(temp.name, "wb") as f_tmp:
                    for line in f:
                        f_tmp.write(line)

            # create file object
            file_type = mimetypes.MimeTypes().guess_type(conf_vars['files'])[0]
            file_obj = v2_wrapper.UploadedFile(
                name="data", filename=temp.name,
                content_type=file_type, original_filename=conf_vars['files'])
            # re-write 'files' parameter in conf_vars
            conf_vars['files'] = file_obj

    # debug of input parameters
    LOG.debug("[DEBUG provided options, conf_vars]: {}".format(conf_vars))

    if CONF.methods.name == 'get_metadata':
        meta = model_obj.get_metadata()
        meta_json = json.dumps(meta)
        LOG.debug("[DEBUG, get_metadata, Output]: {}".format(meta_json))
        if CONF.deepaas_method_output:
            _store_output(meta_json, CONF.deepaas_method_output)

        return meta_json

    elif CONF.methods.name == 'warm':
        # await model_obj.warm()
        model_obj.warm()
        LOG.info("[INFO, warm] Finished warm() method")

    elif CONF.methods.name == 'predict':
        # call predict method
        predict_vars = _get_subdict(conf_vars, predict_args)
        task = model_obj.predict(**predict_vars)

        if CONF.deepaas_method_output:
            out_file = CONF.deepaas_method_output
            out_path = os.path.dirname(os.path.abspath(out_file))
            if not os.path.exists(out_path):  # Create path if does not exist
                os.makedirs(out_path)
            # check extension of the output file
            out_filename, out_extension = os.path.splitext(out_file)

            # set default extension for the data returned
            # by the application to .json
            extension = ".json"
            # check what is asked to return by the application (if --accept)
            if CONF.methods.__contains__('accept'):
                if CONF.methods.accept:
                    extension = mimetypes.guess_extension(CONF.methods.accept)

            if (extension is not None and out_extension is not None
                    and extension != out_extension):          # noqa: W503
                out_file = out_file + extension
                LOG.warn("[WARNING] You are trying to store {} "
                         "type data in the file "
                         "with {} extension!\n"
                         "===================> "
                         "New output is {}".format(extension,
                                                   out_extension,
                                                   out_file))
            if extension == ".json" or extension is None:
                results_json = json.dumps(task)
                LOG.debug("[DEBUG, predict, Output]: {}".format(results_json))
                f = open(out_file, "w+")
                f.write(results_json)
                f.close()
            else:
                out_results = task.name
                shutil.copy(out_results, out_file)

            LOG.info("[INFO, Output] Output is saved in {}".format(out_file))

        return task

    elif CONF.methods.name == 'train':
        train_vars = _get_subdict(conf_vars, train_args)
        start = time.time()
        task = model_obj.train(**train_vars)
        LOG.info("[INFO] Elapsed time:  %s", str(time.time() - start))
        # we assume that train always returns JSON
        results_json = json.dumps(task)
        LOG.debug("[DEBUG, train, Output]: {}".format(results_json))
        if CONF.deepaas_method_output:
            _store_output(results_json, CONF.deepaas_method_output)

        return results_json

    else:
        LOG.warn("[WARNING] No Method was requested! Return get_metadata()")
        meta = model_obj.get_metadata()
        meta_json = json.dumps(meta)
        LOG.debug("[DEBUG, get_metadata, Output]: {}".format(meta_json))

        return meta_json


if __name__ == '__main__':
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main())
    # loop.close()
    main()
