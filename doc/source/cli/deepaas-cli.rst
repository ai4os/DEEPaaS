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
    To get all available flags for the method, one has to call 
    ``deepaas-cli <method> --help``.
    An additional parameter ``--deepaas_model_output`` is available 
    to store the output in a pre-defined by a user file.
    If several models are available for loading, one has to provide 
    which one to load via DEEPAAS_V2_MODEL environment setting.

Options
=======

.. option:: get_metadata

   Calls get_metadata() method. The output can be stored via
   --deepaas_model_output.

.. option:: warm

   Calls warm() method, e.g. to prepare the model for execution.

.. option:: predict

   Calls predict() method. The output can be stored via
   --deepaas_model_output.
   
.. option:: train

   Calls train() method. The output can be stored via
   --deepaas_model_output.

.. option:: --deepaas_model_output 

   To save the results to a local file, if needed. Available for 
   get_metadata, predict, train methods.
  
Files
=====

None

See Also
========

Documentation: `DEEPaaS API <https://docs.deep-hybrid-datacloud.eu/projects/deepaas/>`_

Reporting Bugs
==============

Bugs are managed at `GitHub <https://github.com/indigo-dc/deepaas>`_

