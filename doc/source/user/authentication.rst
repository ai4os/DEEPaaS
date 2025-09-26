.. _authentication:

Bearer Token Authentication
===========================

DEEPaaS supports bearer token authentication for securing API endpoints. When
enabled, all model endpoints and predictions require a valid
``Authorization: Bearer <token>`` header.

Configuration
-------------

Bearer authentication is configured using the ``--auth-bearer-token`` command
line option or the ``auth_bearer_token`` configuration option.

Command Line Usage
~~~~~~~~~~~~~~~~~~

.. code-block:: console

   # Start DEEPaaS with bearer authentication
   deepaas-run --auth-bearer-token my-secret-token

   # Or set via environment variable
   export DEEPAAS_AUTH_BEARER_TOKEN=my-secret-token
   deepaas-run

Configuration File
~~~~~~~~~~~~~~~~~~

Add to your DEEPaaS configuration file:

.. code-block:: ini

   [DEFAULT]
   auth_bearer_token = my-secret-token

Usage
-----

When authentication is enabled, API clients must include the bearer token in
the Authorization header:

.. code-block:: console

   # Example API calls with bearer token
   curl -H "Authorization: Bearer my-secret-token" http://localhost:5000/v2/models/
   curl -H "Authorization: Bearer my-secret-token" -X POST http://localhost:5000/v2/models/my-model/predict

Security Considerations
-----------------------

- Keep your bearer tokens secure and don't share them in logs or version control
- Use strong, randomly generated tokens
- Consider rotating tokens periodically
- The token is transmitted in HTTP headers, so use HTTPS in production

Behavior
--------

**When authentication is disabled** (default)
    All endpoints are accessible without authentication

**When authentication is enabled**
    Model endpoints (``/v2/models/*``) and predict endpoints require valid bearer tokens

**Public endpoints**
    Root endpoint (``/``) and API version endpoint (``/v2/``) remain accessible without authentication

**Invalid/Missing tokens**
    Return HTTP 401 Unauthorized with appropriate error messages

Examples
--------

Python requests
~~~~~~~~~~~~~~~

.. code-block:: python

   import requests

   headers = {"Authorization": "Bearer my-secret-token"}
   response = requests.get("http://localhost:5000/v2/models/", headers=headers)

curl
~~~~

.. code-block:: console

   curl -H "Authorization: Bearer my-secret-token" \
        -X POST \
        -F "data=@image.jpg" \
        http://localhost:5000/v2/models/my-model/predict