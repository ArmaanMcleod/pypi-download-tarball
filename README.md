# PyPI Download Tarball - DEPRECATED

[![PyPI version](https://badge.fury.io/py/pypi-download-tarball.svg)](https://badge.fury.io/py/pypi-download-tarball)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://travis-ci.org/OpticGenius/pypi-download-tarball.svg?branch=master)](https://travis-ci.org/OpticGenius/pypi-download-tarball)

**No longer supporting this repository**

Automates manual Python library installation through the *PyPi* `tar.gz` tarball. If no tarball is found, the program will look for next available `.zip` file and install the package. I've used this in the past when *pip* hasn't worked out, and I have to revert to manual installation of Python libraries. Works on **Python 3.5+**. 

## Install with:

`pip install pypi-download-tarball`

Or:

`python setup.py install`

## Basic Usage

Installing a single package from the command line:

`pypi-download-tarball -p <package name>`

## File Usage

Installing via packages listed on separate lines in a `.txt` file. 

#### Example File Format:

```
xlrd
black
pyinstaller
```

#### Command:

`pypi-download-tarball -r <text file>`

## Demo

![xlrd-example](demo.gif)

## Developement

### Windows

#### Installing Development dependencies

* Run `build install`

#### Running tests:

* Run `build test`, which runs all the unit tests in `tests.py`.

All the other targets are for upload package to PyPi. 

### Linux

#### Installing Development dependencies

* Run `make install`

Make sure you have [GNU Make](https://www.gnu.org/software/make/) installed. You can install it with `sudo apt-get install make`. 

#### Running tests:

* Run `make test`, which runs all the unit tests in `tests.py`.

All the other targets are for upload package to PyPi. 

#### Running tests:

* Run `build test`, which runs all the unit tests in `tests.py`.

All the other targets are for upload package to PyPi. 

## Note
* This tool currently installs the latest version of your package.
* This package is currently is platform independent. It should work on **Windows**, **Linux** and **MacOSX**. 
* If your using a *Unix* enviorment, you might need to use `python3`/`pip3` instead of `python`/`pip`. 
