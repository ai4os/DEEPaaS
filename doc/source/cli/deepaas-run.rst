===========
deepaas-run
===========

Synopsis
========

:program:`deepaas-run` [options]

Description
===========

:program:`deepaas-run` is a server daemon that serves the models that are
   loaded through the ``deepaas.v2.models`` entrypoint API.

Options
=======

All the options can also be set with ``DEEPAAS_<OPTION>`` environment
variables or in a configuration file. Check the
:doc:`configuration reference </install/configuration/config>` for the
complete list.

.. option:: --config-file PATH

   Path to a configuration file to use. It can be given several times.

.. option:: --config-dir DIR

   Path to a directory with configuration files (``*.conf``).

.. option:: --model-name MODEL_NAME

   Specify the model to be used. If not specified, DEEPaaS will fail if there
   are more than only one models available.

.. option:: --listen-ip LISTEN_IP

   IP address on which the DEEPaaS API will listen (default: ``127.0.0.1``).

.. option:: --listen-port LISTEN_PORT

   Port on which the DEEPaaS API will listen (default: ``5000``).

.. option:: --base-path BASE_PATH

   Base path for the API, when it is served behind a reverse proxy that is
   not at the root of the domain (e.g. ``/deepaas``).

.. option:: --debug, -d, --nodebug

   If set, the logging level will be set to DEBUG instead of the default INFO
   level.

.. option:: --debug-endpoint, --nodebug-endpoint

   Enable the ``/v2/debug/`` endpoint, that returns what is printed to the
   standard output and error (default: disabled).

.. option:: --doc-endpoint, --nodoc-endpoint

   Serve the documentation at ``/docs`` and ``/redoc`` (default: enabled).

.. option:: --warm, --nowarm

   Warm (i.e. initialize) the model before serving it (default: enabled).

.. option:: --auth-bearer-token TOKEN

   Require this bearer token to access the model endpoints. Prefer the
   ``DEEPAAS_AUTH_BEARER_TOKEN`` environment variable, as command line
   arguments are visible in the process list. See :ref:`authentication`.

Files
=====

``deepaas.conf`` and ``deepaas-run.conf`` in ``~/.deepaas/``, ``~/``,
``/etc/deepaas/`` or ``/etc/``, and ``*.conf`` files in the
``deepaas.conf.d`` directories in the same locations.


See Also
========

Documentation: `DEEPaaS API <https://docs.deep-hybrid-datacloud.eu/projects/deepaas/>`_

Reporting Bugs
==============

Bugs are managed at `GitHub <https://github.com/indigo-dc/deepaas>`_

