.. _devel-v2:

Integrating a model into the V2 API (CURRENT)
=============================================


.. important::
   V2 of the API (starting on release ``1.0.0`` is the default, supported
   version. It is backwards incomptabile the V1 version.

.. note::
   The current version of the DEEPaaS API is V2. The first release supporting this
   API version was ``1.0.0``. Please do not be confused with the ``deepaas``
   `release` (i.e. ``0.5.2``, ``1.0.0``) and the DEEPaaS API version (V1 or V2).

Defining what to load
---------------------

The DEEPaaS API uses Python's `Setuptools`_ entry points that are dinamycally
loaded to offer the model functionality through the API. This allows you to
offer several models using a single DEEPaaS instance, by defining different
entry points for the different models.

.. _Setuptools: https://setuptools.readthedocs.io/en/latest/setuptools.html

When the DEEPaaS API is spawned it will look for the ``deepaas.v2.model``
entrypoint namespace, loading and adding the names found into the API
namespace. In order to define your entry points, your modulle should leverage
setuptools and be ready to be installed in the system. Then, in order to define
your entry points, you should add the following to your ``setup.cfg``
configuraton file:

.. code-block:: ini

   [entry_points]

   deepaas.v2.model =
       my_model = package_name.module

This will define an entry point in the ``deepaas.v2.model`` namespace, called
``my_model``. All the required functionality will be fetched from the
``package_name.module`` module. This means that ``module`` should provide the
:ref:`model-api` as described below.

If you provide a class with the required functionality, the entry point will be
defined as follows:

.. code-block:: ini

   [entry_points]

   deepaas.v2.model =
       my_model = package_name.module:Class

Again, this will define an entry point in the ``deepaas.v2.model`` namespace,
called ``my_model``. All the required functionality will be fetched
from the ``package_name.module.Class`` class, meaning that an object of
``Class`` will be created and used as entry point. This also means that
``Class`` objects should provide the :ref:`model-api` as described below.

Entry point (model) API
-----------------------
.. _model-api:

Regardless on the way you implement your entry point (i.e. as a module or as an
object), you should expose the following functions or methods:

Defining model medatata
#######################

Your model entry point must implement a ``get_medatata`` function that will
return some basic metadata information about your model, as follows:

.. autofunction:: deepaas.model.v2.base.BaseModel.get_metadata

Training
########

Regarding training there are two functions to be defined. First of all, you can
specify the training arguments to be defined (and published through the API)
with the ``add_train_args`` function, as follows:

.. autofunction:: deepaas.model.v2.base.BaseModel.add_train_args

Then, you must implement the training function (named ``train``) that will
receive the defined arguments as keyword argumetns:

.. autofunction:: deepaas.model.v2.base.BaseModel.train

Prediction and inference
########################

For prediction, there are different functions to be implemented. First of all,
as for the training, you can specify the prediction arguments to be defined,
(and published through the API) with the ``add_predict_args`` as follows:

.. autofunction:: deepaas.model.v2.base.BaseModel.add_predict_args

Do not forget to add an input argument to hold your data. If you want to upload
files for inference to the API, you should use a ``werkzeug.FileStorate`` as
type, for instance::

    def add_predict_args(self, parser):
        parser.add_argument('data',
                            help="Data file to perform inference.",
                            type=werkzeug.FileStorage,
                            location="files",
                            dest='files',
                            required=True)

Then you should define the ``predict`` function as indicated below. You will
receive all the arguments that have been parsed as keyword arguments:

.. autofunction:: deepaas.model.v2.base.BaseModel.predict

By default, the return values from these two functions will be casted into a
string, and will be returned in the following JSON response::

   {
      "status": "OK",
      "predictions": "<model response as string>"
   }

However, it is reccomended that you specify a custom custom response schema.
This way the API exposed will be richer and it will be easier for developers to
build applications against your API, as they will be able to discover the
response schemas from your endpoints.

In order to define a custom response, the ``response`` attribute is used:

.. autodata:: deepaas.model.v2.base.BaseModel.response

   Must contain a valid JSON schema for the model's predictions or None.

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

   For example, if our model performs predictions in the following form::

      {
         "date": "2019-01-1",
         "labels": [
            {"label": "foo", "probability": 1.0},
            {"label": "bar", "probability": 0.7},
         ]
      }

   We should define the following JSON schema::

      response = {
           "$schema": "http://json-schema.org/draft-04/schema#",
           "type": "object",
           "properties": {
               "date": {"type": "string", "format": "date-time"},
               "labels": {
                   "type": "array",
                   "items": {"$ref": "#/definitions/Label"},
               },
           },
           "required": ["labels"],
           "definitions": {
               "Label": {
                   "properties": {
                       "label": {"type": "string"},
                       "probability": {"type": "number"},
                   },
                   "required": ["label", "probability"],
                   "type": "object",
               },
           },
       }


Using classes
-------------

Apart from using a module, you can base your entrypoints on classes. If you
want to do so, you may find useful to inhering from the
``deepaas.model.v2.base.BaseModel`` abstract class:

.. autoclass:: deepaas.model.v2.base.BaseModel
   :members:
