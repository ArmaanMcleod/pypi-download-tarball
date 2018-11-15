# Python Tarball Downloader

Automates manual Python library installation through the *PyPi* `tar.gz` tarball. I've used this in the past when *pip* hasn't worked out, and I have to revert to manual installation of Python libraries.

## Installing Dependencies

Libraries needed are [tqdm](https://pypi.org/project/tqdm/4.28.1/), [requests](https://pypi.org/project/requests/2.20.1/) and [beautifulsoup4](https://pypi.org/project/beautifulsoup4/4.6.3/).

#### Install with:

`pip install -r requirements.txt`

Or:

`make install`

## Basic Usage

Installing a single package from the command line:

`python download.py -p <package name>`

## File Usage

Installing via packages listed on separate lines in a `.txt` file. 

#### Example File Format:

```
xlrd
black
pyinstaller
```

#### Command:

`python download.py -r <text file>`

## Note
* This package currently works on **Windows** and **Linux**.
* If your using *Linux*, you will need to use `python3`/`pip3` instead of `python`/`pip`. 
* Tested on **Python 3**.