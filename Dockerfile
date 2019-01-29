FROM ubuntu:18.04
LABEL maintainer="Alvaro Lopez Garcia <aloga@ifca.unican.es>"
LABEL version="0.2.0"
LABEL description="DEEP as a Service Generic Container"

RUN apt-get update && \
    apt-get upgrade -y

RUN apt-get install -y --no-install-recommends \
        curl \
        python-pip \
        python-dev \
        python-setuptools \
        python3-pip \
        python3-dev \
        python3-setuptools

RUN pip install ansible==2.4
RUN ansible-galaxy install indigo-dc.deepaas
RUN curl -o /tmp/test.yml \
         -L https://github.com/indigo-dc/ansible-role-deepaas/raw/master/tests/test.yml
RUN ansible-playbook -c local -i 'localhost,' /tmp/test.yml

EXPOSE 5000

CMD ["sh", "-c", "deepaas-run --openwhisk --listen-ip 0.0.0.0"]
