.PHONY: help
.PHONY: install

MAKEFLAGS += --no-print-directory

help:
	@echo "Makefile rules:"
	@echo "install - Install dependencies."

install:
	${MAKE} try_first || ${MAKE} otherwise_handle_error

try_first:
	pip install -r requirements.txt

otherwise_handle_error:
	pip3 install -r requirements.txt

