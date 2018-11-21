# Python Tarball Downloader

[![PyPI version](https://badge.fury.io/py/python-tarball-downloader.svg)](https://badge.fury.io/py/python-tarball-downloader)

Automates manual Python library installation through the *PyPi* `tar.gz` tarball. If no tarball is found, the program will look for next available `.zip` file and install the package. I've used this in the past when *pip* hasn't worked out, and I have to revert to manual installation of Python libraries. 

#### Install with:

`pip install python-tarball-downloader`

## Basic Usage

Installing a single package from the command line:

`download -p <package name>`

## File Usage

Installing via packages listed on separate lines in a `.txt` file. 

#### Example File Format:

```
xlrd
black
pyinstaller
```

#### Command:

`download -r <text file>`

## Demo

![xlrd-example](demo.gif)

## Note
* This tool currently installs the latest version of your package.
* This package is currently is platform independent. It should work on **Windows**, **Linux** and **MacOSX**. 
* If your using a *Unix* enviorment, you might need to use `python3`/`pip3` instead of `python`/`pip`. 
* Tested on **Python 3.5+**.