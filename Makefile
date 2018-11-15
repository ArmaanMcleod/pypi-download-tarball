.PHONY: help
.PHONY: install

help:
	@echo "Makefile rules:"
	@echo "install - Install dependencies."

install:
	pip3 install -r requirements.txt