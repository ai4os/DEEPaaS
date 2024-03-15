===========
deepaas-run
===========

Synopsis
========

:program:`deepaas-api` [options]

Description
===========

:program:`deepaas-run` is a server daemon that serves the models that are
   loaded through the ``deepaas.v2.models`` entrypoint API.

Options
=======

.. option:: --model-name MODEL_NAME

    Specify the model to be used. If not specified, DEEPaaS will serve all the models
    that are available. If specified, DEEPaaS will serve only the specified model. You
    can also use the DEEPAAS_V2_MODEL environment variable.

    WARNING: Serving multiple models is deprecated and will be removed in the future,
    therefore it is strongly suggested that you specify the model you want to or that
    you ensure that only one model is available.

.. option:: --debug, -d

   If set to true, the logging level will be set to DEBUG instead of the
   default INFO level.

.. option:: --predict-endpoint

   Specify whether DEEPaaS should provide a train endpoint (default: True).

.. option:: --train-endpoint

   Specify whether DEEPaaS should provide a train endpoint (default: True).

.. option:: --debug-endpoint

   Enable debug endpoint. If set we will provide all the information that you
   print to the standard output and error (i.e. stdout and stderr) through the
   ``/debug`` endpoint. Default is to not provide this information. This will
   not provide logging information about the API itself.

.. option:: --listen-ip LISTEN_IP

   IP address on which the DEEPaaS API will listen. The DEEPaaS API service
   listens on this IP address for incoming requests.

.. option:: --listen-port LISTEN_PORT

   Port on which the DEEPaaS API will listen. The DEEPaaS API service listens
   on this port number for incoming requests.

.. option:: --predict-workers PREDICT_WORKERS, -p PREDICT_WORKERS

   Specify the number of workers to spawn for prediction tasks. If using a CPU
   you probably want to increase this number, if using a GPU probably you want
   to leave it to 1. (defaults to 1)

.. option:: --train-workers TRAIN_WORKERS

   Specify the number of workers to spawn for training tasks. Unless you know
   what you are doing you should leave this number to 1. (defaults to 1)


Files
=====

None

See Also
========

Documentation: `DEEPaaS API <https://docs.deep-hybrid-datacloud.eu/projects/deepaas/>`_

Reporting Bugs
==============

Bugs are managed at `GitHub <https://github.com/indigo-dc/deepaas>`_

