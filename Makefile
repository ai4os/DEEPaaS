VIRTUALENV ?= virtualenv

ifndef VERBOSE
.SILENT:
endif

.PHONY: help
help:
	@echo 'Makefile to run and test the DEEPaaS API                               '
	@echo '                                                                       '
	@echo 'Usage:                                                                 '
	@echo '   make setup      generate a virtualenv and install DEEPaaS inside it '
	@echo '   make develop    generate a virtualenv and install DEEPaaS inside it '
	@echo '	                  in develop mode (i.e. pip install -e )              '
	@echo '   make demo       install the AI4OS demo application in the virtualenv'
	@echo '   make run        execute the API service from the virtualenv, serving'
	@echo '                   the demo application                                '
	@echo '   make regenerate regenerate the virtualenv                           '
	@echo '   make clean      cleanup the existing virtualenv                     '
	@echo '                                                                       '
	@echo 'Environment variables:                                                 '
	@echo '	VIRTUALENV: path for the virtualenv (defaults to "virtualenv")        '

.PHONY: setup
setup: $(VIRTUALENV) 
	. $(VIRTUALENV)/bin/activate; cd $(VIRTUALENV); pip uninstall -y deepaas
	. $(VIRTUALENV)/bin/activate; pip install .

.PHONY: develop
develop: $(VIRTUALENV) 
	. $(VIRTUALENV)/bin/activate; cd $(VIRTUALENV); pip uninstall -y deepaas
	. $(VIRTUALENV)/bin/activate; pip install -e .

#.PHONY: develop
#develop: requirements.txt virtualenv install
#
regenerate: | clean $(VIRTUALENV)

$(VIRTUALENV):
	@echo 'D> Creating $(VIRTUALENV)...'
	python3 -m venv $(VIRTUALENV)

.PHONY: clean 
clean:
	@echo 'D> Deleting $(VIRTUALENV)...'
	rm -rf $(VIRTUALENV)

# The demo application only needs a few of its dependencies to be served, and
# it has to be installed in editable mode, as it reads its metadata from its
# source tree.
.PHONY: demo
demo: $(VIRTUALENV)
	. $(VIRTUALENV)/bin/activate; pip install --no-deps --src $(VIRTUALENV)/src \
		-e git+https://github.com/ai4os-hub/ai4os-demo-app#egg=ai4os-demo-app
	. $(VIRTUALENV)/bin/activate; pip install aiohttp tensorboardX mlflow-skinny pyyaml setuptools

.PHONY: run 
run: setup demo $(VIRTUALENV)
	@echo 'D> Running DEEPaaS inside $(VIRTUALENV)'
	. $(VIRTUALENV)/bin/activate; deepaas-run
