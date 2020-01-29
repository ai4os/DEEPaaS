===========
deepaas-execute
===========

Synopsis
========

:program:`deepaas-execute` [options]

Description
===========

:program:`deepaas-execute` It is a command that allows you to obtain, 
    through the command line, the prediction of a file or the url of 
    a file, of the models that are loaded through the ``deepaas.v2.models``
    entrypoint API.

Options
=======

.. option:: --input_file INPUT_FILE, -i INPUT_FILE

   Set local input file to predict. This option is required.

.. option:: --content_type CONTENT_TYPE, -c CONTENT_TYPE

   Especify the content type of the output file. The
   available options are (image/png, application/json (by
   default), application/zip).

.. option:: --output OUTPUT_DIR, -o OUTPUT_DIR

   Save the result to a local file. This option is required.

.. option:: --url, -u 

   If set to true, the input file is the url o a file to predict.
  
Files
=====

None

See Also
========

Documentation: `DEEPaaS API <https://docs.deep-hybrid-datacloud.eu/projects/deepaas/>`_

Reporting Bugs
==============

Bugs are managed at `GitHub <https://github.com/indigo-dc/deepaas>`_

