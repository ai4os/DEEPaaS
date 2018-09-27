# DEEPaaS

DEEP as a Service (DEEPaaS) is a REST API that is focused on providing access
to machine learning models. By using DEEPaaS users can easily run a REST API
in fron of their model, thus accesing its functionality via HTTP calls.

## Quickstart

The best way to quickly try the DEEPaaS API is trough:

    make run

This command will install a virtualenv (in the `virtualenv` directory) with
DEEPaaS and all its dependencies and will run the DEEPaaS REST API, listening
on `127.0.0.1:5000`. If you browse to `http://127.0.0.1:5000` you will get the
swagger documentation page.

### Develop mode

If you want to run the code in develop mode (i.e. `pip install -e`), you can
issue the following command before:

    make develop
