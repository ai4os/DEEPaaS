.. _devel-v1:


Integrating a model into the V1 API (DEPRECATED)
================================================

.. attention::
   V1 version the API is deprecated and NOT supported starting on release
   ``1.0.0``. Please refer to the :ref:`upgrade-notes` in order to get
   information on how to adapt your model to V2 of the API.

DEEPaaS V1 is based on Python's Setuptools entry points that are dinamically
loaded to offer the model functionality through the API.

When the API is spawned it will look for the deepaas.model entrypoint
namespace, loading and adding the names found into the API namespace. Note that
the names that can be registed into a single namespace are not unique,
therefore the API can load several models at one, offering all of them in the
corresponding namespace in the REST endpoint.

Once loaded, the API exposes the following functions or methods:

* ``get_metadata()``: Get the model metadata.
* ``predict_data(args)``: Perform a prediction using raw data. The API will
  pass a Python dict containing all the necessary information to make a prediction.
  The keys of this dict are:

    * 'files': This is a Werkzeug `FileStorage` object containing the data to predict. You can access the bytes of the data with args['files'].read() or the file extension with args['files'].content_type
    * 'urls': This should be empty for this method
    * other keys needed to make the prediction as defined by the function `get_test_args`

  The response must be a str or a dict
* ``predict_url(args)``: Perform a prediction using URLs. The API will
  pass a Python dict containing all the necessary information to make a prediction.
  The keys of this dict are:

    * 'files': This should be empty for this method
    * 'urls': This is a list of strings of the URLs to use for prediction
    * other keys needed to make the prediction as defined by the function `get_test_args`

  The response can must be a str or a dict
* ``train()``: Perform a training over a dataset.
* ``get_train_args()``: Retrieve the parameters needed for training. This
  method must return a dict of dicts. A possible example is the following:

  .. code-block:: python

      {
         'arg1': {
            'default': '1',   # value must be a string (use json.dumps to convert Python objects)
            'help': '',       # can be an empty string
            'required': False # boolean defining whether the value
                              # must be filled to accept the query
         },
         'arg2': {
            ...
         },
      ...
      }

* ``get_test_args()``: Retrieve the parameters needed for testing. This method
  must return a dict of dicts. Forbidden parameter names are `files` and `urls`. A possible example is the following:

  .. code-block:: python

      {
         'arg1': {
            'default': '1',   # value must be a string (use json.dumps to convert Python objects)
            'help': '',       # can be an empty string
            'required': False # boolean defining whether the value
                              # must be filled to accept the query
         },
         'arg2': {
            ...
         },
      ...
      }


If the API fails to lookup any of these methods it will not silently fail, but
return a 501 Not Implemented HTTP Error.


Example: Exposing a module functionality
----------------------------------------

Suppose that you have under your my_model.api code the following code structure:

.. code-block:: python

   import my_model
   import my_model.whatever

   def get_metadata():
       return my_model.metadata

   def predict_data(data):
       my_model.whatever.do_stuff(data)

You will expose this functionality with the following configuration in your
Setuptools configuration under ``setup.cfg``:

.. code-block:: ini

   [entry_points]

   deepaas.model =
       my_model = my_model.api

Example: Using the DEEPaaS base class
-------------------------------------

For the model developer convenience, DEEPaaS offers the abstract base class
deepaas.models.BaseModel (under the deepaas.models module) that can be
inherited by child classes, overriding the corresponding methods:

.. code-block:: python

   import deepaas.models

   class MyModel(deepaas.models.BaseModel):
       """This is My Model."""

       def get_metadata(self):
           return ...

       (...)

In order to expose this functionality, the entry point should be defined as follows:

.. code-block:: ini

   [entry_points]

   deepaas.model =
       my_model = my_model.api:MyModel

