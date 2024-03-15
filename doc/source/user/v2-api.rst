.. _devel-v2:

Integrating a model into the V2 API (CURRENT)
=============================================

If you want to see an example of a module integrated with deepaas, where those
methods are actually implemented, please head over to the
`deephdc demo app <https://github.com/deephdc/demo_app>`_.

Defining what to load
---------------------

The DEEPaaS API uses Python's `Setuptools`_ entry points that are dynamically
loaded to offer the model functionality through the API. This allows you to
offer several models using a single DEEPaaS instance, by defining different
entry points for the different models.

.. warning::
   Serving multiple models is marked as deprecated, and will be removed in a
   future major version of the API. Please ensure that you start using the `model-name`
   configuration option in your configuration file or the `--model-name` command line
   option as soon as possible.

.. _Setuptools: https://setuptools.readthedocs.io/en/latest/setuptools.html

When the DEEPaaS API is spawned it will look for the ``deepaas.v2.model``
entrypoint namespace, loading and adding the names found into the API
namespace. In order to define your entry points, your module should leverage
setuptools and be ready to be installed in the system. Then, in order to define
your entry points, you should add the following to your ``setup.cfg``
configuration file:

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

.. _model-api:

Entry point (model) API
-----------------------

Regardless on the way you implement your entry point (i.e. as a module or as an
object), you should expose the following functions or methods:

Defining model metadata
#######################

Your model entry point must implement a ``get_medatata`` function that will
return some basic metadata information about your model, as follows:

.. autofunction:: deepaas.model.v2.base.BaseModel.get_metadata
   :no-index:

Warming a model
###############

You can initialize your model before any prediction or train is done by
defining a ``warm`` function. This function receives no arguments and returns
no result, but it will be call before the API is spawned.

You can use it to implement any loading or initialization that your model may
use. This way, your model will be ready whenever a first prediction is done,
reducint the waiting time.

.. autofunction:: deepaas.model.v2.base.BaseModel.warm
   :no-index:

Training
########

Regarding training there are two functions to be defined. First of all, you can
specify the training arguments to be defined (and published through the API)
with the ``get_train_args`` function, as follows:

.. autofunction:: deepaas.model.v2.base.BaseModel.get_train_args
   :no-index:

Then, you must implement the training function (named ``train``) that will
receive the defined arguments as keyword arguments:

.. autofunction:: deepaas.model.v2.base.BaseModel.train
   :no-index:

Prediction and inference
########################

For prediction, there are different functions to be implemented. First of all,
as for the training, you can specify the prediction arguments to be defined,
(and published through the API) with the ``get_predict_args`` as follows:

.. autofunction:: deepaas.model.v2.base.BaseModel.get_predict_args
   :no-index:

Do not forget to add an input argument to hold your data. If you want to upload
files for inference to the API, you should use a ``webargs.fields.Field``
field created as follows::

    def get_predict_args():
        return {
            "data": fields.Field(
                description="Data file to perform inference on.",
                required=False,
                missing=None,
                type="file",
                location="form")
         }

You can also predict data stored in an URL by using::

    def get_predict_args():
        return {
            "url": fields.Url(
                description="Url of data to perform inference on.",
                required=False,
                missing=None)
         }

.. important::
  do not forget to add the ``location="form"`` and ``type="file"`` to the
  argument definition, otherwise it will not work as expected.

Once defined, you will receive an object of the class described below for each
of the file arguments you declare. You can open and read the file stored in the
``filename`` attribute.

.. autoclass:: deepaas.model.v2.wrapper.UploadedFile
   :no-index:

Then you should define the ``predict`` function as indicated below. You will
receive all the arguments that have been parsed as keyword arguments:

.. autofunction:: deepaas.model.v2.base.BaseModel.predict
   :no-index:

By default, the return values from these two functions will be casted into a
string, and will be returned in the following JSON response::

   {
      "status": "OK",
      "predictions": "<model response as string>"
   }

However, it is recommended that you specify a custom response schema.
This way the API exposed will be richer and it will be easier for developers to
build applications against your API, as they will be able to discover the
response schemas from your endpoints.

In order to define a custom response, the ``schema`` attribute is used:

.. autodata:: deepaas.model.v2.base.BaseModel.schema
   :no-index:

Returning different content types
*********************************

Sometimes it is useful to return something different than a JSON file. For such
cases, you can define an additional argument ``accept`` defining the content
types that you are able to return as follows::

    def get_predict_args():
        return {
            'accept': fields.Str(description="Media type(s) that is/are acceptable for the response.",
                                 missing='application/zip',
                                 validate=validate.OneOf(['application/zip', 'image/png', 'application/json']))
         }

Find `in this link <https://www.iana.org/assignments/media-types/media-types.xhtml>`_ a
comprehensive list of possible content types. Then the predict function will have to
return the raw bytes of a file according to the user selection.  For example::


    def predict(**args):
        # Run your prediction

        # Return file according to user selection
        if args['accept'] == 'image/png':
            return open(img_path, 'rb')

        elif args['accept'] == 'application/json':
            return {'some': 'json'}

        elif args['accept'] == 'application/zip':
            return open(zip_path, 'rb')

If you want to return several content types at the same time (let's say a JSON and an image), the easiest way it to
return a zip file with all the files.

Using classes
-------------

Apart from using a module, you can base your entrypoints on classes. If you
want to do so, you may find useful to inhering from the
``deepaas.model.v2.base.BaseModel`` abstract class:

.. autoclass:: deepaas.model.v2.base.BaseModel
   :members:

.. warning::
    The API uses ``multiprocessing`` for handling tasks. Therefore if you use
    decorators around your methods, please follow best practices and use
    `functools.wraps <http://gael-varoquaux.info/programming/decoration-in-python-done-right-decorating-and-pickling.html>`_
    so that the methods are still pickable. Beware also of using global variables
    that might not be shared between processes.
