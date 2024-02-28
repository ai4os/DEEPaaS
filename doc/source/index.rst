DEEPaaS API
===========

Release v\ |version|. (:ref:`Installation <installation>`)

.. image:: https://img.shields.io/pypi/l/deepaas.svg
    :target: https://pypi.org/project/deepaas/

.. image:: https://img.shields.io/pypi/wheel/deepaas.svg
    :target: https://pypi.org/project/deepaas/

.. image:: https://img.shields.io/pypi/pyversions/deepaas.svg
    :target: https://pypi.org/project/deepaas/

DEEP as a Service (DEEPaaS) is a REST API that is focused on providing access
to machine learning models. By using DEEPaaS users can easily run a REST API in
fron of their model, thus accesing its functionality via HTTP calls.

Compatibility
-------------

The DEEPaaS API works with Python 3.5.3 or higher.

Installation and upgrade documentation
--------------------------------------

.. toctree::
   :maxdepth: 2

   install/index

User documentation
-------------------

If you want to try the DEEPaaS API, or if you want to integrate a machine
learning, neural network or deep learning model with it, this documentation is
what you are looking for.

.. toctree::
   :maxdepth: 2

   user/index.rst

API reference
#############

If you are looking for information on a specific function, class or
method, this part of the documentation is for you.

.. toctree::
   :maxdepth: 2

   api

Additional Notes
----------------

.. toctree::
   :maxdepth: 2

   contributing/index


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. # This is needed for things that we need to add to the TOC because otherwise
   # Sphinx will complain
.. toctree::
   :hidden:

   install/configuration/config
   install/configuration/sample
   cli/index
