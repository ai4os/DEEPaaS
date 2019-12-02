.. _upgrade-notes:

Upgrade notes
=============

Upgrading to version 1.0.0
--------------------------

The release ``1.0.0`` of the DEEPaaS API implements several backwards
incompatible changes when compared with the previous releases in the ``0.X.X``
series. Before upgrading your code and deploying into production, read the
following, as changes are needed in your model. Please go through the following
checklist in order.


* **Python version**
  
  The new version of DEEPaaS uses ``aiohttp`` which requires `at least 
  <https://aiohttp.readthedocs.io/en/stable/faq.html#why-is-python-3-5-3-the-lowest-supported-version>`_
  Python 3.5.3. So please update you module accordingly if needed. 

* **Migrate new namespace entry point.**

  Previous code relied on a top-level entry point named ``deepaas.model``,
  where we searched for the required functions or methods to be invoked for
  each API action.

  Now the namespace has changed to ``deepaas.v2.model``.

  Therefore, assuming that your code for V1 of the API was under the
  ``my_model.api`` and you defined your the entry point as follows:

  .. code-block:: ini

    [entry_points]

    deepaas.model =
      my_model = my_model.api

  You should migrate to the following:

  .. code-block:: ini

      [entry_points]

      deepaas.v2.model =
          my_model = my_model.api

  .. note::
    If you do not change the namespace, we will try to load the old
    entrypoint. However, this is deprecated and you should upgrade as soon as
    possible.

* **Migrate from returning dictionaries to use an argument parser to define
  train and predict arguments.**

  Previous code relied on returning arbitrary dictionaries that were used to
  generate the arguments for each of the API endpoints. This is not anymore
  supported and you should return a ``webargs`` field dictionary (check
  `here <https://webargs.readthedocs.io/en/latest/quickstart.html>`_
  for more information. This is still done by defining the ``get_predict_args``
  and ``get_train_args`` functions.  These functions must receive no arguments
  and they should return a dictionary as follows::

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

  .. note::
      If you do still follow the old way of returning the arguments we will try
      to load the arguments using the old ``get_*_args`` functions. However,
      this is DEPRECATED and you should migrate to using the argument parser as
      soon as possible. All the arguments will be converted to Strings,
      therefore you will loose any type checking, etc.

* **Explicitly define your input arguments.**

  The previous version of the API
  defined two arguments for inference: ``data`` and ``urls``. This is not
  anymore true, and you must define your own input arguments.
  To replicate the response of v1 you have to define::

      from webargs import fields

      (...)

      def get_predict_args():
         return {
            'files': fields.Field(
                required=False,
                missing=None,
                type="file",
                data_key="data",
                location="form",
                description="Select the image you want to classify."),

            'urls': fields.Url(
                required=False,
                missing=None,
                description="Select an URL of the image you want to classify.")
                 }

  Then, you will get your input data in the ``data`` and ``urls`` keyword arguments in your
  application.

  .. note::
      For the moment, in contrast with v1, only one url field at the same time is enabled,
      although multi-url (along with multi-files) support is coming soon.

* **Define your responses for the prediction.**

  Now, unless you explicitly define your application response schema,
  whatever you return will be converted into a string and wrapped in the following response::

      {
         "status": "OK",
         "predictions": "<model response as string>"
      }

* **Change in the ``predict`` function name.**

  The ``predict_url`` and ``predict_data`` functions have been merged into a single ``predict``
  function. In addition, arguments are now passed as unpacked keyword arguments, not anymore as a
  dictionary. So if you want to upgrade to v2 with minimal code changes, you just have to add
  the following function to your .py file::

    def predict(**args):

        if (not any([args['urls'], args['files']]) or
                all([args['urls'], args['files']])):
            raise Exception("You must provide either 'url' or 'data' in the payload")

        if args['files']:
            args['files'] = [args['files']]  # patch until list is available
            return predict_data(args)
        elif args['urls']:
            args['urls'] = [args['urls']]  # patch until list is available
            return predict_url(args)

* **Changes in the data response**

  The returned object in ``args['files']`` is no longer a ``werkzeug.FileStorage`` but a
  ``deepaas.model.v2.wrapper.UploadedFile`` which has attributes like ``name`` (name of the 
  argument where this file is being sent), ``filename`` (complete file path to the temporary
  file in the filesystem) and ``content_type`` (content-type of the uploaded file).

  The main difference is that now you should read the bytes using ``open(f.filename, 'rb').read()``
  instead of ``f.read()``.

* **Catch error function**

  By default Exceptions raised in the PREDICT method from the application side will be rendered as
  ``500 - HTTPInternalServerError`` with the message ``Server got itself in trouble``. If you want to
  render some Exceptions with custom status   codes and custom messages (see the ``reason`` arg) you have
  to raise an `aiohttp web exception <https://docs.aiohttp.org/en/latest/web_exceptions.html>`_. For example::

    from aiohttp.web import HTTPBadRequest

    try:
        f()
    except Exception as e:
        raise HTTPBadRequest(reason=e)

  And if you want to wrap a whole function so that any error it raises is passed as a certain HTTP error::

    def catch_error(f):
        def wrap(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                raise HTTPBadRequest(reason=e)
        return wrap


    @catch_error
    def f():
        ...

  .. note::
    Python Exceptions from the application side for the TRAIN method will be correctly rendered
    by DEEPaaS so there is no need to wrap the train function with the catch_error decorator.

* **API url**

  Now the API functions are accessed under http://api_url/docs (eg. http://0.0.0.0:5000/docs)
