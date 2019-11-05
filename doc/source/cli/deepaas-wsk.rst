===========
deepaas-wsk
===========

Synopsis
========

:program:`deepaas-wsk` [options]

Description
===========

:program:`deepaas-wsk` is a server daemon that serves the models that are
   loaded through the ``deepaas.models`` entrypoint as an OpenWhisk action.  API.

Options
=======

.. option:: --debug, -d

   If set to true, the logging level will be set to DEBUG instead of the
   default INFO level.

.. option:: --debug-endpoint

   Enable debug endpoint. If set we will provide all the information that you
   print to the standard output and error (i.e. stdout and stderr) through the
   ``/debug`` endpoint. Default is to not provide this information. This will
   not provide logging information about the API itself.

.. option:: --enable-v1

   Whether to enable V1 version of the API or not. If this option is set to
   ``True``, DEEPaaS API will offer a ``/v1/`` endpoint with the DEPRECATED
   version of the API.

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

