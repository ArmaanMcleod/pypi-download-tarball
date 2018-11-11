# Python Source Downloader

Automates manual Python library installtion through the *PyPi* tarball. I've used this in the past when *pip* hasn't worked out, and I have to revert to manual installation of Python libraries.

## Installing Dependencies

`pip install -r requirements.txt`

## Basic Usage

Installing a single package from the command line:

`python main.py -p <package name>`

## File Usage

Installing via packages listed on separate lines in a `.txt` file. 

### File Format:

```
xlrd
pyinstaller
```

### Example:

`python3 main.py -r packages.txt`

## Note
* This package currently works on **Windows** and **Linux**.
* Uses **Python 3**.