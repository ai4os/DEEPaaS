# DEEPaaS

[![fair-software.eu](https://img.shields.io/badge/fair--software.eu-%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8F-green)](https://fair-software.eu)
[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/9063/badge)](https://www.bestpractices.dev/projects/9063)
[![GitHub license](https://img.shields.io/github/license/ai4os/DEEPaaS.svg)](https://github.com/ai4os/DEEPaaS/blob/master/LICENSE)
[![GitHub release](https://img.shields.io/github/release/ai4os/DEEPaaS.svg)](https://github.com/ai4os/DEEPaaS/releases)
[![PyPI](https://img.shields.io/pypi/v/deepaas.svg)](https://pypi.python.org/pypi/deepaas)
[![Python versions](https://img.shields.io/pypi/pyversions/deepaas.svg)](https://pypi.python.org/pypi/deepaas)
[![Build Status](https://jenkins.services.ai4os.eu/job/AI4OS/job/DEEPaaS/job/master/badge/icon)](https://jenkins.services.ai4os.eu/job/AI4OS/job/DEEPaaS/job/master/)
[![Documentation Status](https://readthedocs.org/projects/deepaas/badge/?version=latest)](https://deepaas.readthedocs.io/en/latest/)
[![DOI](https://joss.theoj.org/papers/10.21105/joss.01517/status.svg)](https://doi.org/10.21105/joss.01517)
[![Zenodo DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.1544377.svg)](https://zenodo.org/doi/10.5281/zenodo.1544377)

<img src="https://raw.githubusercontent.com/ai4os/.github/ai4os/profile/horizontal-transparent.png" width=200 alt="AI4EOSC logo"/>
<img src="https://marketplace.deep-hybrid-datacloud.eu/images/logo-deep.png" width=200 alt="DEEP-Hybrid-DataCloud logo"/>

DEEP as a Service API (DEEPaaS API) is a REST API built on
[aiohttp](https://docs.aiohttp.org/) that allows to provide easy access to
machine learning, deep learning and artificial intelligence models. By using
the DEEPaaS API users can easily run a REST API in front of their model, thus
accessing its functionality via HTTP calls. DEEPaaS API leverages the [OpenAPI
specification](https://github.com/OAI/OpenAPI-Specification).

# Documentation

The DEEPaaS documentation is hosted on [Read the Docs](https://deepaas.readthedocs.io/).


## Quickstart

The best way to quickly try the DEEPaaS API is through:

    make run

This command will install a virtualenv (in the `virtualenv` directory) with
DEEPaaS and all its dependencies and will run the DEEPaaS REST API, listening
on `127.0.0.1:5000`. If you browse to `http://127.0.0.1:5000` you will get the
Swagger documentation page (i.e. the Swagger web UI).

### Develop mode

If you want to run the code in develop mode (i.e. `pip install -e`), you can
issue the following command before:

    make develop


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

# Acknowledgements

This software has been developed within the DEEP-Hybrid-DataCloud (Designing
and Enabling E-infrastructures for intensive Processing in a Hybrid DataCloud)
project that has received funding from the European Union's Horizon 2020
research and innovation programme under grant agreement No 777435.
