===========
deepaas-predict
===========

Synopsis
========

:program:`deepaas-predict` [options]

Description
===========

:program:`deepaas-predict` It is a command that allows you to obtain, 
    through the command line, the prediction of a file or the url of 
    a file, of the models that are loaded through the ``deepaas.v2.models``
    entrypoint API.

Options
=======

.. option:: --input-file INPUT_FILE, -i INPUT_FILE

   Set local input file to predict. This option is required.

.. option:: --content-type CONTENT_TYPE, -c CONTENT_TYPE

   Especify the content type of the output file. The selected
   option must be available in the model used.
   (by default application/json).

.. option:: --model-name CONTENT_TYPE, -c CONTENT_TYPE

   Add the name of the model from which you want
   to obtain the prediction.
   If there are multiple models installed and youd don't
   specify the name of the one you want to use the program will fail.
   If there is only one model installed, that will be used
   to make the prediction.
   
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

