# DEEPaaS

[![GitHub license](https://img.shields.io/github/license/indigo-dc/DEEPaaS.svg)](https://github.com/indigo-dc/DEEPaaS/blob/master/LICENSE)
[![GitHub release](https://img.shields.io/github/release/indigo-dc/DEEPaaS.svg)](https://github.com/indigo-dc/DEEPaaS/releases)
[![PyPI](https://img.shields.io/pypi/v/deepaas.svg)](https://pypi.python.org/pypi/deepaas)
[![Python versions](https://img.shields.io/pypi/pyversions/deepaas.svg)](https://pypi.python.org/pypi/deepaas)

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

## Offering a model through the API

DEEPaaS is based on Python's Setuptools entry points that are dinamically
loaded to offer the model functionality through the API.

When the API is spawned it will look for the `deepaas.model` entrypoint
namespace, loading and adding the names found into the API namespace. Note that
the names that can be registed into a single namespace are not unique,
therefore the API can load several models at one, offering all of them in the
corresponding namespace in the REST endpoint.

Once loaded, the API exposes the following functions or methods:

    * `get_metadata()`: Get the model metadata.
    * `predict_data(data)`: Perform a prediction using raw data. The API will
      pass a single argument that will contain a list of raw data objects to be
      analyzed as a single prediction.
    * `precit_url(urls)`: Perform a predction using urls. The API will pass a
      single argument that will contain a list of urls to be analyzed as a
      single prediction.
    * `train()`: Perform a training over a dataset.

If the API fails to lookup any of these methods it will not silently fail, but
return a `501 Not Implemented` HTTP Error.

### Example: Exposing a module functionality

Suppose that you have under your `my_model.api` code the following code
structure:

    import my_model
    import my_model.whatever

    def get_metadate():
        return my_model.metadata

    def predict_data(data):
        my_model.whatever.do_stuff(data)

You will expose this functionality with the following configuration in your
Setuptools configuration under `setup.cfg`:

    [entry_points]

    deepaas.model =
        my_model = my_model.api

### Example: Using the DEEPaaS base class

For the model developer convenience, DEEPaaS offers the abstract base class
`deepaas.models.BaseModel` (under the `deepaas.models` module) that can be
inherited by child classes, overriding the corresponding methods:

    import deepaas.models

    class MyModel(deepaas.models.BaseModel):
        """This is My Model."""

        def get_metadata(self):
            return ...

        (...)

In order to expose this functionality, the entry point should be defined as
follows:

    [entry_points]

    deepaas.model =
        my_model = my_model.api:MyModel
