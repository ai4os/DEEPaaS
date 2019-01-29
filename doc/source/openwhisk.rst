.. _openwhisk:

DEEPaaS API as an OpenWhisk action
==================================

DEEPaaS API can be executed inside a Docker container as an OpenWhisk Docker
action. In your Dockerfile, you have to ensure that you execute ``deepaas-run``
with the ``--openwhisk-detect`` switch, as follows:

.. code-block:: console

   (...)
   CMD ["sh", "-c", "deepaas-run --openwhisk --listen-ip 0.0.0.0"]

For a complete example, check the `DEEP OC Generic Container
<https://github.com/deephdc/DEEP-OC-generic-container>` or the ``Dockerfile``
that is included within the DEEPaaS API repository.

With that Dockerfile you can build your docker container and create the
corresponding OpenWhisk action:

.. code-block:: console

   docker build -t foobar/container .
   wsk action create action-name --docker foobar/container --web true
