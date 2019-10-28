.. _upgrade-notes:

Upgrade notes
=============

Upgrading to version 1.0.0
--------------------------

The release ``1.0.0`` of the DEEPaaS API implementes several backwards
incompatible changes when compared with the previous releases in the ``0.X.X``
series. Before upgrading your code and deploying into production, read the
following, as changes are needed in your model. Please go through the following
checklist in order.

* Migrate new namespace entry point .

  Previous code relied on a top-level entry point named ``deepaas.model``,
  where we searched for the required functions or methods to be invoked for
  each API action.

  Now the namespace has changed to ``deepaas.v2.model``.

  Therefore, assumming that your code for V1 of the API was under the
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

* Migrate from returning dictionaries to use an argument parser to define
  train and predict arguments.

  Previous code relied on returing arbitrary dictionaries that were used to
  generate the arguments for each of the API endpoints. This is not anymore
  supported and you should return a ``webargs`` field dictioary. This is still
  done by defining the ``get_predict_args`` and ``fet_train_args`` functions.
  These functions must receive no arguments and they should return a dictionary
  as follows::

      from webargs import fields

      (...)

      def get_predict_args():
         return {
            "arg1": fields.Str(
               required=False,
               default="foo",
               description="Argument one"
            ),
         }


  .. note::
      If you do still follow the old way of returning the arguments we will try
      to load the arguments using the old ``get_*_args`` functions. However,
      this is DEPRECATED and you should migrate to using the argument parser as
      soon as possible. All the arguments will be converted to Strings,
      therefore you will loose any type checking, etc.

* Explictly define your input arguments. The previous version of the API
  defined two arguments for inference: ``data`` and ``urls``. This is not
  anymore true, and you must define your own input arguments as follows::

      from webargs import fields

      (...)

      def get_predict_args():
         return {
            "data": fields.Field(
               required=True,
               type="file",
               location="form",
            ),
         }

  Then, you will get your input data in the ``data`` keyword argument in your
  application.

* Define your responses for the prediction. Now, unless you explicitly define
  your application response schema, whatever you return will be converted into
  a string and wrapped in the following response::

      {
         "status": "OK",
         "predictions": "<model response as string>"
      }

* Arguments and now passed as unpacked keyword arguments, not anymore as a
  dictionary.
