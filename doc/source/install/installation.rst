.. _installation:

Installation
============

The recommended way to install the DEEPaaS API is with ``pip``:

.. code-block:: console

   pip install deepass

This way you will ensure that the stable version is fetched from pip, rather
than development or unstable version

Installing the development version
----------------------------------

The development version of DEEPaas can be installed from the ``master`` brach
of the `GitHub DEEPaaS repository <https://github.com/indigo-dc/deepaas>`_ and
can be installed as follows (note the ``-e`` switch to install it in editable
or "develop mode"):

.. code-block:: console

   git clone https://github.com/indigo-dc/DEEPaaS
   cd DEEPaaS
   pip install -e
