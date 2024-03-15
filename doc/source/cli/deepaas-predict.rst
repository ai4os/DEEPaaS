================
deepaas-predict
================

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

.. option:: --model-name MODEL_NAME

    Specify the model to be used. If not specified, DEEPaaS will serve all the models
    that are available. If specified, DEEPaaS will serve only the specified model. You
    can also use the DEEPAAS_V2_MODEL environment variable.

    WARNING: Serving multiple models is deprecated and will be removed in the future,
    therefore it is strongly suggested that you specify the model you want to or that
    you ensure that only one model is available.

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

