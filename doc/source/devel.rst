.. _devel:


Integrating a model into the API
=================================

DEEPaaS is based on Python's Setuptools entry points that are dinamically
loaded to offer the model functionality through the API.

When the API is spawned it will look for the deepaas.model entrypoint
namespace, loading and adding the names found into the API namespace. Note that
the names that can be registed into a single namespace are not unique,
therefore the API can load several models at one, offering all of them in the
corresponding namespace in the REST endpoint.

Once loaded, the API exposes the following functions or methods:

* ``get_metadata()``: Get the model metadata.
* ``predict_data(data)``: Perform a prediction using raw data. The API will
  pass a single argument that will contain a list of raw data objects to be
  analyzed as a single prediction.
* ``precit_url(urls)``: Perform a predction using urls. The API will pass a
  single argument that will contain a list of urls to be analyzed as a
  single prediction.
* ``train()``: Perform a training over a dataset.
* ``get_train_args()``: Retrieve the parameters needed for training. This method must return a dict of dicts. A possible
  example is the following:

  .. code-block:: python

      { 'arg1' : {'default': '1',     #value must be a string (use json.dumps to convert Python objects and json.loads to convert back)
                  'help': '',         #can be an empty string
                  'required': False   #bool (whether or not the user must fill the parameter, for example if there is no default)
                 },
        'arg2' : {...
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

