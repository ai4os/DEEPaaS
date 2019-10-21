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
  supported and you should add your options explicitly. This is done by
  defining the ``add_predict_args`` and ``add_train_args`` functions. These
  functions will receive a single argument containing a `argparse`_-like object
  that you should use to define the arguments, e.g.::

   def add_predict_args(parser):
      parser.add_argument("parameter",
                          type=int,
                          required=False,
                          default=0,
                          help="A parameter for the predict method")

  .. _argparse: https://docs.python.org/3/library/argparse.html

  .. note::
      If you do not implement these functions we will try to load the arguments
      using the old ``get_*_args`` functions. However, this is DEPRECATED and
      you should migrate to using the argument parser as soon as possible. If
      both functions are defined, we will only take into account the arguments
      added through the ``add_*_args`` functions.


* Define your responses for the prediction, as defined in...
