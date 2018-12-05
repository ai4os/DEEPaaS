# DEEPaaS

[![GitHub license](https://img.shields.io/github/license/indigo-dc/DEEPaaS.svg)](https://github.com/indigo-dc/DEEPaaS/blob/master/LICENSE)
[![GitHub release](https://img.shields.io/github/release/indigo-dc/DEEPaaS.svg)](https://github.com/indigo-dc/DEEPaaS/releases)
[![PyPI](https://img.shields.io/pypi/v/deepaas.svg)](https://pypi.python.org/pypi/deepaas)
[![Python versions](https://img.shields.io/pypi/pyversions/deepaas.svg)](https://pypi.python.org/pypi/deepaas)
[![Build Status](https://jenkins.indigo-datacloud.eu:8080/buildStatus/icon?job=Pipeline-as-code/DEEPaaS/master)](https://jenkins.indigo-datacloud.eu:8080/job/Pipeline-as-code/job/DEEPaaS/job/master/)

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

# Documentation

The DEEPaaS documentation is hosted on [Read the Docs](https://deepaas.readthedocs.io/).
