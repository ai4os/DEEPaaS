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
import argparse
import ast
import deepaas
import io
import json
import mimetypes
import multiprocessing as mp
import os
import re
import sys
import tempfile
import uuid

from datetime import datetime
from marshmallow import fields  # marshmallow
from oslo_config import cfg
from oslo_log import log

from deepaas import config
from deepaas.model import loading
from deepaas.model.v2 import wrapper as v2_wrapper

CONF = config.CONF

LOG = log.getLogger(__name__)

debug_cli = False

# Not all types are covered! If not listed, the type is 'str'
# see https://marshmallow.readthedocs.io/en/stable/marshmallow.fields.html

# Passing lists or dicts with argparse is not straight forward, so we use pass them as
# string and parse them with `ast.literal_eval`
# ref: https://stackoverflow.com/questions/7625786/type-dict-in-argparse-add-argument
# We follow a similar approach with bools
# ref: https://stackoverflow.com/a/59579733/18471590
# ref: https://stackoverflow.com/questions/715417/converting-from-a-string-to-boolean-in-python/18472142#18472142  # noqa


def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")


FIELD_TYPE_CONVERTERS = {
    fields.Bool: str2bool,
    fields.Boolean: str2bool,
    fields.Date: str,
    fields.DateTime: str,
    fields.Dict: ast.literal_eval,
    fields.Email: str,
    fields.Float: float,
    fields.Int: int,
    fields.Integer: int,
    fields.List: ast.literal_eval,
    fields.Str: str,
    fields.String: str,
    fields.Time: str,
    fields.URL: str,
    fields.Url: str,
    fields.UUID: str,
    fields.Field: str,
}


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
        # initialise param with no "default", type "str" (!), empty "help"
        param = {"default": None, "type": str, "help": ""}

        # Initialize help string
        val_help = val.metadata.get("description", "")
        if "%" in val_help:
            # argparse hates % sign:
            # replace single occurancies of '%' with '%%'
            # since "%%"" is accepted by argparse
            val_help = re.sub(r"(?<!%)%(?!%)", r"%%", val_help)

        # Infer "type"
        val_type = type(val)
        if val_type in FIELD_TYPE_CONVERTERS:
            param["type"] = FIELD_TYPE_CONVERTERS[val_type]

        if val_type is fields.List:
            val_help += '\nType: list, enclosed as string: "[...]"'
        elif val_type is fields.Dict:
            val_help += '\nType: dict, enclosed as string: "{...}"'
        elif val_type in [fields.Bool, fields.Boolean]:
            val_help += "\nType: bool"
        else:
            val_help += f"\nType: {param['type'].__name__}"
        if val_type is fields.Field:
            if val.metadata.get("type", "") == "file":
                val_help += " (filepath)"
            else:
                val_help += " (WARNING: original type fields.Field)"

        # Infer "required"
        param["required"] = val.required
        if not val.required:
            param["default"] = val.missing
            val_help += f"\nDefault: {val.missing}"
        else:
            val_help += "\n*Required*"

        # Add choices to help message
        if "enum" in val.metadata.keys():
            val_help += f"\nChoices: {val.metadata['enum']}"

        val_help = val_help.lstrip("\n")  # remove escape when no description found
        param["help"] = val_help

        dict_out[key] = param

    return dict_out


# Function to detect file arguments
def _get_file_args(fields_in):
    """Function to retrieve a list of file-type fields
    :param fields_in: mashmallow fields
    :return: list
    """
    file_fields = []
    for k, v in fields_in.items():
        if (type(v) is fields.Field) and (v.metadata.get("type", "") == "file"):
            file_fields.append(k)

    return file_fields


# Function to get a model object
def _get_model_name():
    """Return et mode name and model fron configured model.

    In case of error, prints the list of available models
    :return: mode name, model object
    """
    model_name = CONF.model_name
    models = loading.get_available_models("v2")
    if model_name:
        model_obj = models.get(model_name)
        if model_obj is None:
            sys.stderr.write(
                "[ERROR]: The model {} is not available.\n"
                "Available models: {}\n".format(model_name, list(models.keys()))
            )
            sys.exit(1)

        return model_name, model_obj

    elif len(models) == 1:
        return models.popitem()

    else:
        sys.stderr.write(
            "[ERROR]: There are several models available ({}).\n"
            "You have to choose one and set it in the DEEPAAS_V2_MODEL "
            "environment variable or using the --mode-name option"
            ".\n".format(list(models.keys()))
        )
        sys.exit(1)


# Get the model name
model_name, model_obj = _get_model_name()

# use deepaas.model.v2.wrapper.ModelWrapper(). deepaas>1.2.1dev4
# model_obj = v2_wrapper.ModelWrapper(name=model_name,
#                                    model_obj=model_obj)

# Once we know the model name,
# we get arguments for predict and train as dictionaries
predict_args = _fields_to_dict(model_obj.get_predict_args())
train_args = _fields_to_dict(model_obj.get_train_args())

# Find which of the arguments are going to be files
file_args = {}
file_args["predict"] = _get_file_args(model_obj.get_predict_args())
file_args["train"] = _get_file_args(model_obj.get_train_args())


# Function to add later these arguments to CONF via SubCommandOpt
def _add_methods(subparsers):
    """Function to add argparse subparsers via SubCommandOpt (see below)
    for DEEPaaS methods get_metadata, warm, predict, train
    """

    # Use RawTextHelpFormatter to allow for line breaks in argparse help messages.
    def help_formatter(prog):
        return argparse.RawTextHelpFormatter(prog, max_help_position=10)

    # in case no method requested, we return get_metadata(). check main()
    subparsers.required = False

    get_metadata_parser = subparsers.add_parser(  # noqa: F841
        "get_metadata",
        help="get_metadata method",
        formatter_class=help_formatter,
    )

    get_warm_parser = subparsers.add_parser(  # noqa: F841
        "warm",
        help="warm method, e.g. to " "prepare the model for execution",
        formatter_class=help_formatter,
    )

    # get predict arguments configured
    predict_parser = subparsers.add_parser(
        "predict",
        help="predict method, use " "predict --help for the full list",
        formatter_class=help_formatter,
    )

    for key, val in predict_args.items():
        predict_parser.add_argument(
            "--%s" % key,
            default=val["default"],
            type=val["type"],
            help=val["help"],
            required=val["required"],
        )
    # get train arguments configured
    train_parser = subparsers.add_parser(
        "train",
        help="train method, use " "train --help for the full list",
        formatter_class=help_formatter,
    )

    for key, val in train_args.items():
        train_parser.add_argument(
            "--%s" % key,
            default=val["default"],
            type=val["type"],
            help=val["help"],
            required=val["required"],
        )


# Now options to be registered with oslo_config
cli_opts = [
    # intentionally long to avoid a conflict with opts from predict, train etc
    cfg.StrOpt(
        "deepaas_method_output",
        help="Define an output file, if needed",
    ),
    cfg.BoolOpt(
        "deepaas_with_multiprocessing",
        default=True,
        help="Activate multiprocessing; default is True",
    ),
    cfg.SubCommandOpt(
        "methods",
        title="methods",
        handler=_add_methods,
        help='Use "<method> --help" to get '
        "more info about options for "
        "each method",
    ),
]

CONF.register_cli_opts(cli_opts)


# store DEEPAAS_METHOD output in a file
def _store_output(results, out_file):
    """Function to store model results in the file
    :param results:  what to store (JSON expected)
    :param out_file: in what file to store
    """

    out_path = os.path.dirname(os.path.abspath(out_file))
    if not os.path.exists(out_path):  # Create path if does not exist
        os.makedirs(out_path)

    with open(out_file, "w+") as f:
        f.write(results)


def main():
    """Executes model's methods with corresponding parameters"""

    # we may add deepaas config, but then too many options...
    # config.config_and_logging(sys.argv)

    log.register_options(CONF)
    log.set_defaults(default_log_levels=log.get_default_log_levels())

    CONF(sys.argv[1:], project="deepaas", version=deepaas.extract_version())
    log.setup(CONF, "deepaas-cli")

    LOG.info(f"{CONF.methods.name} was called.")

    # put all variables in dict, makes life easier...
    conf_vars = vars(CONF._namespace)

    if CONF.deepaas_with_multiprocessing:
        mp.set_start_method("spawn", force=True)

    # Create file wrapper for file args, ONLY for "predict()" and "train()"
    if CONF.methods.name == "predict" or CONF.methods.name == "train":
        # Create file wrapper for file args (if provided!)
        for farg in file_args[CONF.methods.name]:
            if getattr(CONF.methods, farg, None):
                fpath = conf_vars[farg]

                # create tmp file as later it supposed
                # to be deleted by the application
                temp = tempfile.NamedTemporaryFile()
                temp.close()
                # copy original file into tmp file
                with open(fpath, "rb") as f:
                    with open(temp.name, "wb") as f_tmp:
                        for line in f:
                            f_tmp.write(line)

                # create file object
                file_type = mimetypes.MimeTypes().guess_type(fpath)[0]
                file_obj = v2_wrapper.UploadedFile(
                    name="data",
                    filename=temp.name,
                    content_type=file_type,
                    original_filename=fpath,
                )
                # re-write parameter in conf_vars
                conf_vars[farg] = file_obj

    # debug of input parameters
    LOG.debug("[provided options, conf_vars]: {}".format(conf_vars))

    if CONF.methods.name == "get_metadata":
        meta = model_obj.get_metadata()
        meta_json = json.dumps(meta)
        LOG.debug("[get_metadata]: {}".format(meta_json))
        if CONF.deepaas_method_output:
            _store_output(meta_json, CONF.deepaas_method_output)

        LOG.info(f"return: {meta_json}")

    elif CONF.methods.name == "warm":
        # await model_obj.warm()
        model_obj.warm()
        LOG.info("return: Finished warm() method")

    elif CONF.methods.name == "predict":
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
            if CONF.methods.__contains__("accept"):
                if CONF.methods.accept:
                    extension = mimetypes.guess_extension(CONF.methods.accept)

            if (
                extension is not None
                and out_extension is not None
                and extension != out_extension
            ):  # noqa: W503
                out_file = out_file + extension
                LOG.warn(
                    "You are trying to store {} "
                    "type data in the file "
                    "with {} extension!\n"
                    "===================> "
                    "New output is {}".format(extension, out_extension, out_file)
                )
            if extension == ".json" or extension is None:
                results_json = json.dumps(task)
                LOG.debug("[predict]: {}".format(results_json))
                _store_output(results_json, out_file)
            elif type(task) is io.BytesIO:
                with open(out_file, "wb") as f:
                    f.write(task.getbuffer())
            else:
                LOG.info(f"Output of type type({task}), {task}")

            LOG.info(f"return: Output is saved in {out_file}")
        else:
            LOG.info(f"return: {task}")

    elif CONF.methods.name == "train":
        train_vars = _get_subdict(conf_vars, train_args)
        # structure of ret{} copied from api.v2.train.build_train_response !!!
        # so far, one needs to sync manually the structures
        start = datetime.now()
        ret = {
            "date": str(start),
            "args": train_vars,
            "status": "done",
            "uuid": uuid.uuid4().hex,
            "result": {},
        }
        task = model_obj.train(**train_vars)
        end = datetime.now()
        ret["result"]["finish_date"] = str(end)
        ret["result"]["duration"] = str(end - start)
        # we assume that train always returns JSON
        ret["result"]["output"] = task
        results_json = json.dumps(ret)
        LOG.info("Elapsed time:  %s", str(end - start))
        LOG.debug("[train]: {}".format(results_json))
        if CONF.deepaas_method_output:
            _store_output(results_json, CONF.deepaas_method_output)
            LOG.info(f"return: Output is saved in {CONF.deepaas_method_output}")
        else:
            LOG.info(f"return: {results_json}")

    else:
        LOG.warn("No Method was requested! Return get_metadata()")
        meta = model_obj.get_metadata()
        meta_json = json.dumps(meta)
        LOG.debug("[get_metadata]: {}".format(meta_json))

        LOG.info(f"return: {meta_json}")


if __name__ == "__main__":
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main())
    # loop.close()
    main()
