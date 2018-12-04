.. _quickstart:

Quickstart
==========

The best way to quickly try the DEEPaaS API is by issuing the following command
(no installation required):

.. code-block:: console

   make run

This command will create a `Python virtualenv
<https://virtualenv.pypa.io/en/latest/>`_ (in the ``virtualenv`` directory)
with DEEPaaS along all its dependencies. Then it will run the DEEPaaS REST API,
listening on ``http://127.0.0.1:5000``. If you browse to that URL you will get
the Swagger UI documentation page.

If you want to run the code in the editable or develop mode (i.e. the same
environment that you would get with ``pip install -e``), you can issue the
following command before:

.. code-block:: console

   make develop

