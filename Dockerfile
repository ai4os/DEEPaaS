FROM ubuntu:18.04
LABEL maintainer="Alvaro Lopez Garcia <aloga@ifca.unican.es>"
LABEL version="0.1.0"
LABEL description="DEEP as a Service Generic Container"

RUN apt-get update && \
    apt-get upgrade -y

RUN apt-get install -y --no-install-recommends \
        git \
        curl \
        python-setuptools \
        python-pip \
        python-wheel \
        python3-setuptools \
        python3-pip \
        python3-wheel

ADD . /srv
WORKDIR /srv

# We can use pip or pip3, depending on the python version that we want to use
RUN pip install .

EXPOSE 5000

CMD deepaas-run
