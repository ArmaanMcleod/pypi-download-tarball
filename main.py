import tarfile

from sys import exit

from time import sleep

from requests import get
from requests.exceptions import RequestException

from bs4 import BeautifulSoup

from argparse import ArgumentParser

from os.path import exists
from os.path import join
from os.path import basename

from os import name
from os import getcwd
from os import chdir

from tempfile import TemporaryDirectory

from shutil import move
from subprocess import Popen
from subprocess import DEVNULL

from tqdm import tqdm

from math import ceil

# Global variables defined here
ROOT_URL = "https://pypi.org/project/"
ROOT_PATH = getcwd()
EXTENSION = ".tar.gz"
CHUNK_SIZE = 1024

# Runnable commands depending if Windows or Linux
OS_COMMANDS = {
    "posix": ["python3", "setup.py", "install", "--user"],
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

        # Iterate through all <a> tags with hrefs
        for a in soup.find_all("a", href=True):
            file_link = a["href"]

            # Download first tar.gz file
            if file_link.endswith(EXTENSION):
                download_file(package, file_link, temp_dir)
                break

    except RequestException as error:
        print(error)
        exit(1)


def parse_file(filename):
    """
    Parses each line from file and inserts into list.
    """

    with open(filename) as file:
        return [line.strip() for line in file.readlines()]

def download_file(package, url, temp_dir):
    """
    Downloads file and inserts into temporary folder.
    """

    print("Requesting %s..." % url)
    response = get(url, stream=True)
    filename = basename(url)
    path = join(temp_dir, filename)

    print("Downloading %s..." % filename)
    total_size = int(response.headers.get("content-length", 0))
    bytes_wrote = 0
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

    print("Unzipping %s..." % filename)
    with tarfile.open(path) as tar:
        tar.extractall()

    # Extract file prefix
    tar_name, _, _ = basename(tar.name).rsplit(".", 2)
    move(join(ROOT_PATH, tar_name), temp_dir)

    # Check that setup.py exists
    chdir(join(temp_dir, tar_name))
    if not exists("setup.py"):
        print("setup.py for package %s does not exist" % package)
        exit(1)

    print("Installing %s..." % package)

    # Call setup.py depending on OS
    Popen(OS_COMMANDS[name], stderr=DEVNULL, stdout=DEVNULL)
    for _ in tqdm(range(100)):
        sleep(0.02)

    # Make sure to return to original current working directory
    # Ensures we can delete contents of temp folder safely
    chdir(ROOT_PATH)


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
