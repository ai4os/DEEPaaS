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

import abc

import six


@six.add_metaclass(abc.ABCMeta)
class BaseModel(object):
    """Base class for all models to be used with DEEPaaS.

    Note that it is not needed for DEEPaaS to inherit from this abstract base
    class in order to expose the model functionality, but the entrypoint that
    is configured should expose the same API.
    """

    response = None
    """Must contain a valid JSON schema for the model's predictions or None.

    The format should be a JSON schema (DRAFT 4)

    In order to provide a consistent API specification we use this attribute to
    define the schema that all the prediction responses will follow.

    If this attribute is set we will validate them against it.

    If it is not set (i.e. ``response = None``), the model's response will be
    converted into a string and the response will have the following form::

        {
            "status": "OK",
            "predictions": "<model response as string>"
        }
    """

    @abc.abstractmethod
    def get_metadata(self):
        """Return metadata from the exposed model.

        The metadata that is expected should follow the schema that is shown
        below. This basically means that you should return a dictionary with
        the folling aspect::

            {
                'author': 'Author name',
                'description': 'Model description',
                'license': 'Model's license',
                'url': 'URL for the model (e.g. GitHub repository)',
                'version': 'Model version',
            }

        The only fields that are mandatory are 'description' and 'name'.

        The JSON schema that we are following is the following::

            {
                'properties': {
                    'author': {
                        'description': 'Model author',
                        'type': 'string'
                    },
                    'description': {
                        'description': 'Model description',
                        'type': 'string'
                    },
                    'license': {'
                        description': 'Model license',
                        'type': 'string'
                    },
                    'name': {
                        'description': 'Model name',
                        'type': 'string'
                    },
                    'url': {
                        'description': 'Model url',
                        'type': 'string'
                    },
                    'version': {
                        'description': 'Model version',
                        'type': 'string'}
                    },
                'required': ['description', 'name'],
                'type': 'object'
            }

        :return: dictionary containing the model's metadata.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def predict(self, **kwargs):
        """Prediction from incoming keyword arguments.

        :param kwargs: The keyword arguments that the predict method accepts
            must be defined by the ``add_predict_args()`` method so the API is
            able to pass them down.

        :return: The response can be a str, a dict or a file (using for example
            ``flask.send_file``)
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def add_predict_args(self, parser):
        """Populate the arguments that are needed to test the application.

        This method should return the parser that is passed as argument.

        :param parser: An argument parser like object, that can be used to
            pupulate the prediction arguments.

        :return: A parser containing the prediction arguments.
        """
        return parser

    @abc.abstractmethod
    def train(self, **kwargs):
        """Perform a training.

        :param kwargs: The keyword arguments that the predict method accepts
            must be defined by the ``add_train_args()`` method so the API is
            able to pass them down. Usually you would populate these with all
            the training hyper-parameters

        :return: TBD
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def add_train_args(self, parser):
        """Populate the arguments that are needed to train the application.

        This method should return the parser that is passed as argument.

        :param parser: An argument parser like object, that can be used to
            pupulate the training arguments.

        :return: A parser containing the training arguments.
        """
        return parser
