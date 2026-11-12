===========
deepaas-cli
===========

Synopsis
========

:program:`deepaas-cli` [options] {get_metadata,warm,predict} [method options]

Description
===========

:program:`deepaas-cli` Command line interface (CLI) to DEEPaaS models
    that are loaded through the ``deepaas.v2.models`` entrypoint API. One gets access
    to the same get_metadata, warm, predict methods with all corresponding options as
    with DEEPaaS REST API.  To get available for the method
    options, one has to call
    ``deepaas-cli <method> --help``.
    Additional parameters are provided:
    ``--deepaas_method_output`` is to store the output in a pre-defined
    by a user file;
    ``--deepaas_with_multiprocessing`` is to activate multiprocessing
    support, default is True.
    If several models are available for loading, one has to provide
    which one to load via the ``--model-name`` option or the
    ``DEEPAAS_MODEL_NAME`` environment variable.

Options
=======

.. option:: get_metadata

   Calls get_metadata() method. The output can be stored via
   --deepaas_method_output.

.. option:: warm

   Calls warm() method, e.g. to prepare the model for execution.

.. option:: predict

   Calls predict() method. The output can be stored via
   --deepaas_method_output. If the model returns a file (e.g. using
   ``--accept image/*``) and no output file is given, its contents are
   written to the standard output.

.. option:: --deepaas_method_output

   To save the results to a local file, if needed. Available for
   get_metadata, predict methods.

.. option:: --deepaas_with_multiprocessing, --nodeepaas_with_multiprocessing

   To activate multiprocessing support, default is True.

.. option:: --debug, -d

   Set the logging level to DEBUG.

.. option:: --config-file PATH

   Path to a configuration file to read the options from.

.. option:: --model-name MODEL_NAME

    Specify the model to be used. If not specified, DEEPaaS will fail if there are
    more than only one models available.

Files
=====

None

See Also
========

Documentation: `DEEPaaS API <https://docs.deep-hybrid-datacloud.eu/projects/deepaas/>`_

Reporting Bugs
==============

Bugs are managed at `GitHub <https://github.com/indigo-dc/deepaas>`_

