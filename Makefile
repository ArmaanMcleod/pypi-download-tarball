.PHONY: help
.PHONY: install
.PHONY: setup

MAKEFLAGS += --no-print-directory

help:
	@echo "Makefile rules:"
	@echo "install - Install dependencies."
	@echo "setup - Setup source distribution and wheel."

install:
	${MAKE} pip_try_first || ${MAKE} pip_handle_error

pip_try_first:
	pip install -r requirements.txt

pip_handle_error:
	pip3 install -r requirements.txt

setup:
	${MAKE} setup_try_first || ${MAKE} setup_handle_error

setup_try_first:
	python setup.py sdist
	python setup.py bdist_wheel

setup_handle_error:
	python3 setup.py sdist
	python3 setup.py bdist_wheel