.PHONY: help
.PHONY: install
.PHONY: clean
.PHONY: setup
.PHONY: upload
.PHONY: test

MAKEFLAGS += --no-print-directory

help:
	@echo "Makefile rules:"
	@echo "install - Install dependencies."
	@echo "clean - Clean generated directories."
	@echo "setup - Setup source distribution and wheel."
	@echo "upload - Upload source distribution and wheel to PyPi."
	@echo "test - Run sample tests."

install:
	${MAKE} pip_try_first || ${MAKE} pip_handle_error

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf download_tarball.egg-info

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

test:
	${MAKE} test_try_first || ${MAKE} test_try_error

test_try_first:
	python tests.py

test_try_error:
	python3 tests.py

upload:
	twine upload dist/*