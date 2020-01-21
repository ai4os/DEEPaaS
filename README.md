# DEEPaaS

[![GitHub license](https://img.shields.io/github/license/indigo-dc/DEEPaaS.svg)](https://github.com/indigo-dc/DEEPaaS/blob/master/LICENSE)
[![GitHub release](https://img.shields.io/github/release/indigo-dc/DEEPaaS.svg)](https://github.com/indigo-dc/DEEPaaS/releases)
[![PyPI](https://img.shields.io/pypi/v/deepaas.svg)](https://pypi.python.org/pypi/deepaas)
[![Python versions](https://img.shields.io/pypi/pyversions/deepaas.svg)](https://pypi.python.org/pypi/deepaas)
[![Build Status](https://jenkins.indigo-datacloud.eu/buildStatus/icon?job=Pipeline-as-code%2FDEEPaaS%2Fmaster)](https://jenkins.indigo-datacloud.eu/job/Pipeline-as-code/job/DEEPaaS/job/master/)
[![DOI](https://joss.theoj.org/papers/10.21105/joss.01517/status.svg)](https://doi.org/10.21105/joss.01517)

<img src="https://marketplace.deep-hybrid-datacloud.eu/images/logo-deep.png" width=200 alt="DEEP-Hybrid-DataCloud logo"/>

DEEP as a Service (DEEPaaS) is a REST API that is focused on providing access
to machine learning models. By using DEEPaaS users can easily run a REST API
in front of their model, thus accessing its functionality via HTTP calls.

## Quickstart

The best way to quickly try the DEEPaaS API is through:

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


# Citing

[![DOI](https://joss.theoj.org/papers/10.21105/joss.01517/status.svg)](https://doi.org/10.21105/joss.01517)

If you are using this software and want to cite it in any work, please use the
following:

> Lopez Garcia, A. "DEEPaaS API: a REST API for Machine Learning and
> Deep Learning models". In: _Journal of Open Source Software_ 4(42) (2019),
> pp. 1517. ISSN: 2475-9066. DOI: [10.21105/joss.01517](https://doi.org/10.21105/joss.01517)

You can also use the following BibTeX entry:

    @article{Lopez2019DEEPaaS,
        journal = {Journal of Open Source Software},
        doi = {10.21105/joss.01517},
        issn = {2475-9066},
        number = {42},
        publisher = {The Open Journal},
        title = {DEEPaaS API: a REST API for Machine Learning and Deep Learning models},
        url = {http://dx.doi.org/10.21105/joss.01517},
        volume = {4},
        author = {L{\'o}pez Garc{\'i}a, {\'A}lvaro},
        pages = {1517},
        date = {2019-10-25},
        year = {2019},
        month = {10},
        day = {25},}
