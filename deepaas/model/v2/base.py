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

    schema = None
    """Must contain a valid schema for the model's predictions or None.

    A valid schema is either a ``marshmallow.Schema`` subclass or a dictionary
    schema that can be converted into a schema.

    In order to provide a consistent API specification we use this attribute to
    define the schema that all the prediction responses will follow, therefore:
    - If this attribute is set we will validate them against it.
    - If it is not set (i.e. ``schema = None``), the model's response will
      be converted into a string and the response will have the following
      form::

          {
              "status": "OK",
              "predictions": "<model response as string>"
          }

    As previously stated, there are two ways of defining an schema here. If our
    response have the following form::

        {
            "status": "OK",
            "predictions": [
                {
                    "label": "foo",
                    "probability": 1.0,
                },
                {
                    "label": "bar",
                    "probability": 0.5,
                },
            ]
        }

    We should define or schema as schema as follows:


    - Using a schema dictionary. This is the most straightforward way. In order
      to do so, you must use the ``marshmallow`` Python module, as follows::

        from marshmallow import fields

        schema = {
            "status": fields.Str(
                        description="Model predictions",
                        required=True
            ),
            "predictions": fields.List(
                fields.Nested(
                    {
                        "label": fields.Str(required=True),
                        "probability": fields.Float(required=True),
                    },
                )
            )
        }

    - Using a ``marshmallow.Schema`` subclass. Note that the schema *must* be
      the class that you have created, not an object::

        import marshmallow
        from marshmallow import fields

        class Prediction(marshmallow.Schema):
            label = fields.Str(required=True)
            probability = fields.Float(required=True)

        class Response(marshmallow.Schema):
            status = fields.Str(
                description="Model predictions",
                required=True
            )
            predictions = fields.List(fields.Nested(Prediction))

        schema = Response
    """

    @abc.abstractmethod
    def get_metadata(self):
        """Return metadata from the exposed model.

        The metadata that is expected should follow the schema that is shown
        below. This basically means that you should return a dictionary with
        the following aspect::

            {
                "author": "Author name",
                "description": "Model description",
                "license": "Model's license",
                "url": "URL for the model (e.g. GitHub repository)",
                "version": "Model version",
            }

        The only fields that are mandatory are 'description' and 'name'.

        The schema that we are following is the following::

            {
                "id": =  fields.Str(required=True,
                                    description='Model identifier'),
                "name": fields.Str(required=True,
                                   description='Model name'),
                "description": fields.Str(required=True,
                                          description='Model description'),
                "license": fields.Str(required=False,
                                      description='Model license'),
                "author": fields.Str(required=False,
                                     description='Model author'),
                "version": fields.Str(required=False,
                                      description='Model version'),
                "url": fields.Str(required=False,
                                  description='Model url'),
                "links": fields.List(
                    fields.Nested(
                        {
                            "rel": fields.Str(required=True),
                            "href": fields.Url(required=True),
                        }
                    )
                )
            }

        :return: dictionary containing the model's metadata.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def predict(self, **kwargs):
        """Prediction from incoming keyword arguments.

        :param kwargs: The keyword arguments that the predict method accepts
            must be defined by the ``get_predict_args()`` method so the API
            is able to pass them down.

        :return: The response must be a str or a dict.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def get_predict_args(self):
        """Return the arguments that are needed to perform a prediction.

        This function should return a dictionary of ``webargs`` fields (check
        `here <https://webargs.readthedocs.io/en/latest/quickstart.html>`_
        for more information). For example::

            from webargs import fields

            (...)

            def get_predict_args():
                return {
                    "arg1": fields.Str(
                        required=False,  # force the user to define the value
                        missing="foo",  # default value to use
                        enum=["choice1", "choice2"],  # list of choices
                        description="Argument one"  # help string
                    ),
                }

        :return dict: A dictionary of ``webargs`` fields containing the
            application required arguments.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def train(self, **kwargs):
        """Perform a training.

        :param kwargs: The keyword arguments that the predict method accepts
            must be defined by the ``get_train_args()`` method so the API is
            able to pass them down. Usually you would populate these with all
            the training hyper-parameters

        :return: TBD
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def get_train_args(self):
        """Return the arguments that are needed to train the application.

        This function should return a dictionary of ``webargs`` fields (check
        `here <https://webargs.readthedocs.io/en/latest/quickstart.html>`_
        for more information). For example::

            from webargs import fields

            (...)

            def get_train_args():
                return {
                    "arg1": fields.Str(
                        required=False,  # force the user to define the value
                        missing="foo",  # default value to use
                        enum=["choice1", "choice2"],  # list of choices
                        description="Argument one"  # help string
                    ),
                }

        :return dict: A dictionary of ``webargs`` fields containing the
            application required arguments.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def warm(self):
        """Warm (initialize, load) the model.

        This is called when the model is loaded, before the API is spawned.

        If implemented, it should prepare the model for execution. This is
        useful for loading it into memory, perform any kind of preliminary
        checks, etc.
        """
        raise NotImplementedError()
