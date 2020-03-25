===========
deepaas-cli
===========

Synopsis
========

:program:`deepaas-cli` [options]

Description
===========

:program:`deepaas-cli` Command line interface (CLI) to DEEPaaS models 
    that are loaded through the ``deepaas.v2.models`` entrypoint API.
    One gets access to the same get_metadata, warm, predict, and train 
    methods with all corresponding options as with DEEPaaS REST API.
    To get available for the method options, one has to call 
    ``deepaas-cli <method> --help``.
    Additional parameters are provided:
    ``--deepaas_method_output`` is to store the output in a pre-defined 
    by a user file; 
    ``--deepaas_with_multiprocessing`` is to activate multiprocessing 
    support, default is True.
    oslo_log package is used for logging information, which provides 
    additional options for the script.
    If several models are available for loading, one has to provide 
    which one to load via DEEPAAS_V2_MODEL environment setting.

Options
=======

.. option:: get_metadata

   Calls get_metadata() method. The output can be stored via
   --deepaas_method_output.

.. option:: warm

   Calls warm() method, e.g. to prepare the model for execution.

.. option:: predict

   Calls predict() method. The output can be stored via
   --deepaas_method_output.
   
.. option:: train

   Calls train() method. The output can be stored via
   --deepaas_method_output.

.. option:: --deepaas_method_output 

   To save the results to a local file, if needed. Available for 
   get_metadata, predict, train methods.

.. option:: --deepaas_with_multiprocessing 

   To activate multiprocessing support, default is True.
  
Files
=====

None

See Also
========

Documentation: `DEEPaaS API <https://docs.deep-hybrid-datacloud.eu/projects/deepaas/>`_

Reporting Bugs
==============

Bugs are managed at `GitHub <https://github.com/indigo-dc/deepaas>`_

