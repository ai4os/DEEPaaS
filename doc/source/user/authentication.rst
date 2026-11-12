.. _authentication:

Bearer token authentication
===========================

DEEPaaS can protect the model endpoints with a bearer token. When it is
enabled, requests to the model endpoints (``/v2/models/*``, including
predictions) and to the debug endpoint (``/v2/debug/``) must include an
``Authorization: Bearer <token>`` header, otherwise they will get a
``401 Unauthorized`` error.

The following endpoints are always public, so that clients can discover the
API and use the interactive documentation:

* The version endpoints (``/`` and ``/v2/``).
* The OpenAPI specification (``/openapi.json`` and ``/swagger.json``).
* The documentation (``/docs`` and ``/redoc``), if enabled. You can use the
  *Authorize* button of the Swagger UI to set the token.

Configuration
-------------

Authentication is disabled by default, and it is enabled by setting a token
with the ``auth_bearer_token`` option in the DEEPaaS configuration file:

.. code-block:: ini

   [DEFAULT]
   auth_bearer_token = my-secret-token

or with the ``DEEPAAS_AUTH_BEARER_TOKEN`` environment variable:

.. code-block:: console

   export DEEPAAS_AUTH_BEARER_TOKEN=my-secret-token
   deepaas-run

It can also be set with the ``--auth-bearer-token`` command line option, but
this is not recommended, as the token will be visible in the process list.

Usage
-----

Clients must include the token in the ``Authorization`` header:

.. code-block:: console

   curl -H "Authorization: Bearer my-secret-token" \
        http://localhost:5000/v2/models/

   curl -H "Authorization: Bearer my-secret-token" \
        -X POST \
        -F "data=@image.jpg" \
        http://localhost:5000/v2/models/my-model/predict

or, using Python:

.. code-block:: python

   import requests

   headers = {"Authorization": "Bearer my-secret-token"}
   response = requests.get("http://localhost:5000/v2/models/", headers=headers)

Security considerations
-----------------------

* Use a strong, randomly generated token, e.g. generated with
  ``python -c "import secrets; print(secrets.token_urlsafe(32))"``.
* Do not store the token in version control.
* The token is sent in an HTTP header, so serve the API over HTTPS (e.g.
  behind a reverse proxy) when it is exposed to the Internet.
