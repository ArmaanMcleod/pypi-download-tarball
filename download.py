import tarfile

from sys import exit
from sys import modules

from time import sleep

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
from os import listdir

from tempfile import TemporaryDirectory

from shutil import move

from subprocess import call
from subprocess import DEVNULL

from threading import Thread

from tqdm import tqdm

from math import ceil

from zipfile import ZipFile

# Global variables defined here
ROOT_URL = "https://pypi.org/project/"
ROOT_PATH = getcwd()
CHUNK_SIZE = 1024

TAR_EXTENSION, ZIP_EXTENSION = ".tar.gz", ".zip"

# Runnable commands depending if Windows or Linux
OS_COMMANDS = {
    "posix": ["python3", "setup.py", "--user"],
    "nt": ["python", "setup.py", "install"],
}


def extract_html(package, url, temp_dir):
    """
    Extracts HTML from web page.
    """

    print("Requesting %s..." % url)

    # Attempt to GET request webpage
    try:

        html_page = get(url)
        html_page.raise_for_status()

        print("Request successful")

        # Create Beautiful soup parser
        soup = BeautifulSoup(html_page.text, features="html.parser")

        found = False

        # Iterate through all <a> tags with hrefs
        for a in soup.find_all("a", href=True):
            file_link = a["href"]

            # Download first tar.gz file
            if file_link.endswith(TAR_EXTENSION):
                download_file(
                    package=package,
                    url=file_link,
                    temp_dir=temp_dir,
                    runner=extract_tarball,
                )
                found = True
                break

            # If no tar.gz file, Download first .zip
            elif file_link.endswith(ZIP_EXTENSION):
                download_file(
                    package=package,
                    url=file_link,
                    temp_dir=temp_dir,
                    runner=extract_zip,
                )
                found = True
                break

        # Source file not found, can't do anything else
        if not found:
            print(
                "%s or %s source file could not be found from %s..."
                % (TAR_EXTENSION, ZIP_EXTENSION, url)
            )
            exit(1)

    except RequestException as error:
        print(error)
        exit(1)


def parse_file(filename):
    """
    Parses each line from file and inserts into list.
    """

    with open(filename) as file:
        return list(map(str.strip, file.readlines()))


def download_file(package, url, temp_dir, runner):
    """
    Downloads file and inserts into temporary folder.
    """

    print("Requesting %s..." % url)
    response = get(url, stream=True)
    filename = basename(url)
    path = join(temp_dir, filename)

    # Run background thread to download file
    print("Downloading %s..." % filename)
    download_thread = Thread(target=run_download(filename, response, path), args=())
    download_thread.daemon = True
    download_thread.start()

    # Run background thread to extract .tar.gz or .zip file
    print("Extracting %s..." % filename)
    extract_thread = Thread(
        target=runner(path=path, temp_dir=temp_dir, package=package), args=()
    )
    extract_thread.daemon = True
    extract_thread.start()

    # Run background thread to install library
    print("Installing %s..." % package)
    print("Please wait...")
    process_thread = Thread(target=run_setup(OS_COMMANDS[name]), args=())
    process_thread.daemon = True
    process_thread.start()

    # Make sure to return to original current working directory
    # Ensures we can delete contents of temp folder safely
    chdir(ROOT_PATH)


def run_download(filename, response, path):
    """
    Downloads file from path using response.
    """

    total_size = int(response.headers.get("content-length", 0))
    bytes_wrote = 0

    # Write out downloaded file
    with open(path, "wb") as file:
        for chunk in tqdm(
            response.iter_content(chunk_size=CHUNK_SIZE),
            total=ceil(total_size // CHUNK_SIZE),
            unit="KB",
            unit_scale=True,
        ):
            if chunk:
                bytes_wrote += len(chunk)
                file.write(chunk)

    if total_size != 0 and bytes_wrote != total_size:
        print("Failed to download %s" % filename)
        exit(1)


def run_setup(commands):
    """
    Runs setup.py commands.
    """
    call(commands, shell=False, stderr=DEVNULL, stdout=DEVNULL)
    for _ in tqdm(range(100)):
        sleep(0.2)


def extract_zip(path, temp_dir, package):
    """
    Extracts zip file and moves it to temporary directory
    """

    # Extract zip file into directory
    with ZipFile(path) as zip_file:
        for file in tqdm(zip_file.namelist(), total=len(zip_file.namelist())):
            zip_file.extract(file, temp_dir)

    # Extract file prefix
    filename = basename(path)
    zip_name, _ = splitext(filename)

    # Check that setup.py exists
    chdir(join(temp_dir, zip_name))
    if not exists("setup.py"):
        print("setup.py for package %s does not exist" % package)
        exit(1)


def extract_tarball(path, temp_dir, package):
    """
    Extracts tar file and moves it to temporary directory.
    """

    # Extract tar file into directory
    with tarfile.open(path) as tar:
        for member in tqdm(tar.getmembers(), total=len(tar.getmembers())):
            tar.extract(member)

    # Extract file prefix
    tar_name, _, _ = basename(tar.name).rsplit(".", 2)
    move(join(ROOT_PATH, tar_name), temp_dir)

    # Check that setup.py exists
    chdir(join(temp_dir, tar_name))
    if not exists("setup.py"):
        print("setup.py for package %s does not exist" % package)
        exit(1)


def main():
    """
    Everything run from here.
    """

    # Configure command line arguements
    parser = ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-p", "--package", type=str)
    group.add_argument("-r", "--requirements", type=str)
    args = parser.parse_args()

    # Create temporary directory and start processing
    with TemporaryDirectory() as temp_dir:
        if args.package:
            url = ROOT_URL + args.package + "/#files"
            extract_html(args.package, url, temp_dir)
            print("%s has been installed." % args.package)
        else:
            packages = parse_file(args.requirements)
            for package in packages:
                url = ROOT_URL + package + "/#files"
                extract_html(package, url, temp_dir)
                print("%s has been installed." % package)


if __name__ == "__main__":
    main()
