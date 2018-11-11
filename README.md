# Python Source Downloader

Automates manual Python library installation through the *PyPi* tarball. I've used this in the past when *pip* hasn't worked out, and I have to revert to manual installation of Python libraries.

## Installing Dependencies

`pip install -r requirements.txt`

## Basic Usage

Installing a single package from the command line:

`python main.py -p <package name>`

## File Usage

Installing via packages listed on separate lines in a `.txt` file. 

#### Example File Format:

```
xlrd
black
pyinstaller
```

#### Command:

`python main.py -r <text file>`

## Note
* This package currently works on **Windows** and **Linux**.
* If your using *Linux*, you will need to use `python3`/`pip3` instead of `python`/`pip`. 
* Tested on **Python 3**.