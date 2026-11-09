===================
Configuration Guide
===================

DEEPaaS options can be set in the command line, with environment variables or
in a configuration file, in that order of precedence. For example, the port
where the API listens can be set with any of the following:

.. code-block:: console

   $ deepaas-run --listen-port 8080

   $ export DEEPAAS_LISTEN_PORT=8080
   $ deepaas-run

   $ cat /etc/deepaas/deepaas.conf
   [DEFAULT]
   listen_port = 8080
   $ deepaas-run

Configuration files use the INI format, with all the options in the
``[DEFAULT]`` section. If no file is given with the ``--config-file`` option,
DEEPaaS reads the first ``deepaas.conf`` (and ``deepaas-run.conf``) file found
in ``~/.deepaas/``, ``~/``, ``/etc/deepaas/`` and ``/etc/``, as well as all the
``*.conf`` files in the ``deepaas.conf.d`` directories in the same locations.
Additional directories can be given with the ``--config-dir`` option.

Environment variables are named ``DEEPAAS_<OPTION>``, with the option name in
upper case and dashes replaced with underscores (e.g. ``DEEPAAS_MODEL_NAME``).

* :doc:`Config Reference <config>`: A complete reference of all
  configuration options available in the ``deepaas.conf`` file.

* :doc:`Sample Config File <sample>`: A sample config
  file with inline documentation.

