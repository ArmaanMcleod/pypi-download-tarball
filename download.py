# Copyright (c) 2018 Armaan McLeod
# This script is part of the download-tarball package.
# Released under a MIT License.

import tarfile

import sys

from requests import get
from requests.exceptions import RequestException

from bs4 import BeautifulSoup

from argparse import ArgumentParser

from os.path import exists
from os.path import join
from os.path import basename
from os.path import splitext

from os import name
from os import getcwd
from os import chdir

from tempfile import TemporaryDirectory

from shutil import move

from subprocess import Popen
from subprocess import PIPE
from subprocess import CalledProcessError

from time import sleep

from tqdm import tqdm

from math import ceil

from zipfile import ZipFile

from sys import executable

from contextlib import contextmanager
from contextlib import suppress

# Global variables defined here
ROOT_URL = "https://pypi.org/project/"
FILE_LOCATION = "/#files"
ROOT_PATH = getcwd()
CHUNK_SIZE = 1024

# Source file extensions
TAR_EXTENSION, ZIP_EXTENSION = ".tar.gz", ".zip"

# Scripts called in program
SETUP_SCRIPT, REQUIREMENTS_FILE = "setup.py", "requirements.txt"

# Install requirements command
REQUIREMENTS_COMMAND = [
    executable,
    "-m",
    "pip",
    "install",
    "-r",
    REQUIREMENTS_FILE,
    "--user",
]

# Setup installation command
SETUP_COMMAND = [executable, SETUP_SCRIPT, "install", "--user"]


@contextmanager
def request_url(url, stream):
    """Handles requests to URL

    Manages HTTP GET requests to url using context manager.
    Allows convenient reuse throughout code. 

    Args:
        url (str): The URL to scrape package source file
        stream (bool): Indicates whether download stream is needed

    Yields:
        requests.models.Request: The response header from HTTP request

    Raises:
        RequestException: If error occured in HTTP GET request to url
        SystemExit: If no source file could be retrieved or HTTP GET request failed.

    """

    response = get(url=url, stream=stream)

    try:
        response.raise_for_status()
        yield response
    except RequestException as error:
        print(error)
        sys.exit(0)


@contextmanager
def subprocess_popen(command):
    """Handles opening a process for a command

    Catches KeyboardInterrupt exception while in process, since child process will
    still throw this exception even if parent process catches it.

    Args:
        command (list): The command to excecute

    Yields:
        subprocess.Popen: The process to execute

    Raises:
        SystemExit: If process was interrupted by KeyboardInterrupt.
    """
    try:
        yield Popen(
            args=command, shell=False, stdout=PIPE, bufsize=1, universal_newlines=True
        )
    except KeyboardInterrupt:
        sys.exit(0)


def extract_html(package, url, directory):
    """Extracts HTML from web page.

    Scrapes URL for file to download. Looks for .tar.gz file first, and
    if none are present, look for .zip file to download. If none of these
    are present, can't proceed with installation.

    Args:
        package (str): The package to install
        url (str): The URL to scrape package source file
        directory (str): The temporary directory to store file

    """

    print("Requesting %s" % url)

    # Attempt to GET request webpage
    with request_url(url=url, stream=False) as html_page:
        print("Request successful")

        # Create Beautiful soup parser
        soup = BeautifulSoup(html_page.text, features="html.parser")

        candidate_links = {TAR_EXTENSION: None, ZIP_EXTENSION: None}

        # Iterate through all <a> tags with hrefs
        # Also add .tar.gz and .zip extensions found
        for a in soup.find_all("a", href=True):
            file_link = a["href"]

            if file_link.endswith(TAR_EXTENSION):
                candidate_links[TAR_EXTENSION] = file_link
            elif file_link.endswith(ZIP_EXTENSION):
                candidate_links[ZIP_EXTENSION] = file_link

        # Priority one: tar.gz file
        if candidate_links.get(TAR_EXTENSION):
            download_file(
                package=package,
                url=candidate_links[TAR_EXTENSION],
                directory=directory,
                extractor=extract_tarball,
            )

        # Priority two: zip file
        elif candidate_links.get(ZIP_EXTENSION):
            download_file(
                package=package,
                url=candidate_links[ZIP_EXTENSION],
                directory=directory,
                extractor=extract_zip,
            )

        # None of the above, this pypi package is unreliable
        else:
            print(
                "%s or %s source file could not be found from %s"
                % (TAR_EXTENSION, ZIP_EXTENSION, url)
            )
            sys.exit(0)


def parse_file(filename):
    """Parse file contents.

    Parses each line from file and inserts into list. 

    Args:
        filename (str): The file to parse
    
    Returns:
        list: Nested list containing rows of file.

    """

    lines = []

    with open(file=filename) as file:
        for line in map(str.strip, file):

            # split on '=' incase the file is given in 'package==...' form
            lines.append(line.split("=")[0])

    return lines


def download_file(package, url, directory, extractor):
    """Downloads file from URL.

    Downloads file specified at URL and inserts into temporary folder.

    Args:
        package (str): The package to install
        url (str): The URL to scrape package source file
        directory (str): The temporary directory to store file
        extractor (function): The function to run for extracting the file

    """

    print("Requesting %s" % url)

    # Attempt to download source file
    with request_url(url=url, stream=False) as response:
        filename = basename(url)
        path = join(directory, filename)

        print("Downloading %s" % filename)
        run_download(filename=filename, response=response, path=path)

        print("Extracting %s" % filename)
        extractor(path=path, directory=directory, package=package),

        if exists(REQUIREMENTS_FILE):
            print("Installing dependencies")
            run_process(command=REQUIREMENTS_COMMAND)

        print("Installing", package)
        run_process(command=SETUP_COMMAND)

        # Make sure to return to original current working directory
        # Ensures we can delete contents of temp folder safely
        chdir(path=ROOT_PATH)


def run_download(filename, response, path):
    """Runs Download of file

    Downloads file from path using HTTP response header data 
    and writes it to path specified.

    Args:
        filename (str): The file to download
        response (requests.models.Request): The response header from HTTP request
        path (str): The path to write file to

    Returns:
        str: The path of the downloaded file

    Raises:
        SystemExit: If download was unsuccessful

    """

    total_size = int(response.headers.get("content-length", 0))
    bytes_wrote = 0

    # Write out downloaded file
    # Display progress bar while at it
    with open(file=path, mode="wb") as file:
        for chunk in tqdm(
            iterable=response.iter_content(chunk_size=CHUNK_SIZE),
            total=ceil(total_size // CHUNK_SIZE),
            unit="KB",
            unit_scale=True,
        ):
            if chunk:
                bytes_wrote += len(chunk)
                file.write(chunk)

    # Make sure the bytes and total size are equal
    # Otherwise file not fully written
    if total_size != 0 and bytes_wrote != total_size:
        print("Failed to download %s" % filename)
        sys.exit(0)

    return file.name


def run_process(command):
    """ Runs Process

    Runs command in opened process in background

    Args:
        command (list): A list of commands to excecute

    Returns:
        int: The return code of the process ran

    Raises:
        CalledProcessError: If the process opened could not be called

    """

    # Process command and log each line from stdout
    # This is needed to find any errors in installation
    with subprocess_popen(command=command) as process:
        lines = list(process.stdout)
        for _ in tqdm(iterable=lines, total=len(lines)):
            sleep(0.1)

    returncode = process.returncode
    if returncode != 0:
        raise CalledProcessError(returncode=returncode, cmd=process.args)

    return returncode


def extract_zip(path, directory, package):
    """Extracts zip file.

    Extracts zip file and moves it to temporary directory. Also checks if
    setup.py exists and switches to temporary directory context.

    Args:
        package (str): The package to install
        path (str): The path of the zip file
        directory (str): The temporary directory to store file

    Returns:
        str: The path of zip file extracted

    Raises:
        SystemExit: If setup.py does not exist, we can't perform installation

    """

    # Extract zip file into directory
    # Moved automatically into temporary directory
    with ZipFile(file=path) as zip_file:
        for file in tqdm(iterable=zip_file.namelist(), total=len(zip_file.namelist())):
            zip_file.extract(member=file, path=directory)

    # Extract file prefix
    filename = basename(path)
    zip_name, _ = splitext(filename)
    zip_path = join(directory, zip_name)

    # Switch to directory and Check that setup.py exists
    # Running setup.py from a path for some reason doesn't work
    chdir(path=zip_path)
    if not exists(path=SETUP_SCRIPT):
        print("%s for package %s does not exist" % (SETUP_SCRIPT, package))
        sys.exit(0)

    return zip_path


def extract_tarball(path, directory, package):
    """Extracts tar compressed file.

    Extracts tar compressed file and moves it to temporary directory. Also checks if
    setup.py exists and switches to temporary directory context.

    Args:
        package (str): The package to install
        path (str): The path of the zip file
        directory (str): The temporary directory to store file

    Returns:
        str: The path of tar file extracted

    Raises:
        SystemExit: If setup.py does not exist, we can't perform installation
        
    """

    # Extract tar file into directory
    # Will store directory into current working directory
    with tarfile.open(name=path) as tar:
        for member in tqdm(iterable=tar.getmembers(), total=len(tar.getmembers())):
            tar.extract(member=member)

    # Extract file prefix
    tar_name, _, _ = basename(tar.name).rsplit(".", 2)
    tar_path = join(directory, tar_name)

    # Move directory into temporary directory
    # Avoids flooding current working directory with too many folders
    move(src=join(ROOT_PATH, tar_name), dst=directory)

    # Switch to directory and Check that setup.py exists
    # Running setup.py from a path for some reason doesn't work
    chdir(path=tar_path)
    if not exists(path=SETUP_SCRIPT):
        print("%s for package %s does not exist" % (SETUP_SCRIPT, package))
        sys.exit(0)

    return tar_path


def main():
    """ Main program run from here.

    Handles initiation of script and processes command line arguements.
    Also creates temporary directory used throughout program.

    """

    # Configure command line arguements
    parser = ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-p", "--package", type=str)
    group.add_argument("-r", "--requirements", type=str)
    args = parser.parse_args()

    # Create temporary directory and start processing
    with TemporaryDirectory() as directory:

        # If one package specified
        if args.package:
            url = ROOT_URL + args.package + FILE_LOCATION
            extract_html(package=args.package, url=url, directory=directory)
            print(args.package, "installed\n")

        # Otherwise, a file must have been supplied
        else:
            packages = parse_file(filename=args.requirements)
            for package in packages:
                url = ROOT_URL + package + FILE_LOCATION
                extract_html(package=package, url=url, directory=directory)
                print(package, "installed\n")

    print("Packages installed. You should now be able to import them.")


if __name__ == "__main__":
    with suppress(BaseException):
        main()
