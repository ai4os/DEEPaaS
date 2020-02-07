.. _predict:

DEEPaaS API as a command line action
==================================

Support for execution from the command line for DEEPaaS. In your Dockerfile, 
you must ensure that you execute `` deepaas-predict`` in one of the following ways:

Basic form of execution.

.. code-block:: console

   (...)
   CMD ["sh", "-c", "deepaas-predict -i INPUT_FILE -o OUTPUT_DIR"]

Execution specifying a content type option.

.. code-block:: console

   (...)
   CMD ["sh", "-c", "deepaas-predict -i INPUT_FILE -c CONTENT_TYPE -o OUTPUT_DIR"]

Execution specifying an url as an input file.

.. code-block:: console

   (...)
   CMD ["sh", "-c", "deepaas-predict -i INPUT_FILE --url -o OUTPUT_DIR"]

Execution specifying the name of a model.

.. code-block:: console

   (...)
   CMD ["sh", "-c", "deepaas-predict -i INPUT_FILE --model-name MODEL_NAME -o OUTPUT_DIR"]

