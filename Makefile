.PHONY: help
.PHONY: install
.PHONY: clean
.PHONY: setup
.PHONY: upload
.PHONY: test

MAKEFLAGS += --no-print-directory

help:
	@echo "Usage: make (rule)"
	@echo "Makefile rules:"
	@echo "install - Install dependencies."
	@echo "clean - Clean generated directories."
	@echo "setup - Setup source distribution and wheel."
	@echo "upload - Upload source distribution and wheel to PyPi."
	@echo "test - Run sample tests."

install:
	pip3 install -r requirements.txt

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf download_tarball.egg-info

setup:
	python3 setup.py sdist
	python3 setup.py bdist_wheel

test:
	python3 tests.py

upload:
	twine upload dist/*