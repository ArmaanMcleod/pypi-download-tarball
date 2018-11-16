import tarfile

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

from threading import Thread

from tqdm import tqdm

from math import ceil

from zipfile import ZipFile

# Global variables defined here
ROOT_URL = "https://pypi.org/project/"
FILE_LOCATION = "/#files"
ROOT_PATH = getcwd()
CHUNK_SIZE = 1024

# Source file extensions
TAR_EXTENSION, ZIP_EXTENSION = ".tar.gz", ".zip"

# Install requirements command
REQUIREMENTS_COMMAND = ["pip3", "install", "-r", "requirements.txt"]

# Scripts called in program
SETUP_SCRIPT, REQUIREMENTS_FILE = "setup.py", "requirements.txt"

# Runnable commands depending if Windows or Linux
OS_COMMANDS = {
    "posix": ["python3", "setup.py", "--user"],
    "nt": ["python", "setup.py", "install"],
}


def extract_html(package, url, temp_dir):
    """
    Extracts HTML from web page.
    """

    print("Requesting %s" % url)

    # Attempt to GET request webpage
    try:

        html_page = get(url)
        html_page.raise_for_status()

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
                temp_dir=temp_dir,
                runner=extract_tarball,
            )

        # Priority two: zip file
        elif candidate_links.get(ZIP_EXTENSION):
            download_file(
                package=package,
                url=candidate_links[ZIP_EXTENSION],
                temp_dir=temp_dir,
                runner=extract_zip,
            )

        # None of the above, this pypi package is unreliable
        else:
            print(
                "%s or %s source file could not be found from %s"
                % (TAR_EXTENSION, ZIP_EXTENSION, url)
            )
            raise SystemExit

    except RequestException as error:
        print(error)
        raise SystemExit


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

    print("Requesting %s" % url)

    # Attempt to download source file
    try:
        response = get(url, stream=True)
        response.raise_for_status()

        filename = basename(url)
        path = join(temp_dir, filename)

        # Run background thread to download file
        print("Downloading %s" % filename)
        download_thread = Thread(
            target=run_download(filename=filename, response=response, path=path),
            args=(),
        )
        download_thread.daemon = True
        download_thread.start()

        # Run background thread to extract .tar.gz or .zip file
        print("Extracting %s" % filename)
        extract_thread = Thread(
            target=runner(path=path, temp_dir=temp_dir, package=package), args=()
        )
        extract_thread.daemon = True
        extract_thread.start()

        # Insert pre requirements install command if it exists
        commands = [OS_COMMANDS[name]]
        if exists(REQUIREMENTS_FILE):
            commands.insert(0, REQUIREMENTS_COMMAND)

        # Run background thread to install library
        print("Installing %s" % package)
        process_thread = Thread(target=run_setup(commands), args=())
        process_thread.daemon = True
        process_thread.start()

        # Make sure to return to original current working directory
        # Ensures we can delete contents of temp folder safely
        chdir(ROOT_PATH)

    except RequestException as error:
        print(error)
        raise SystemExit


def run_download(filename, response, path):
    """
    Downloads file from path using response.
    """

    total_size = int(response.headers.get("content-length", 0))
    bytes_wrote = 0

    # Write out downloaded file
    # Display progress bar while at it
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

    # Make sure the bytes and total size are equal
    # Otherwise file not fully written
    if total_size != 0 and bytes_wrote != total_size:
        print("Failed to download %s" % filename)
        raise SystemExit


def run_setup(commands):
    """
    Runs setup.py commands.
    """

    # Process each command and log each line from stdout
    # This is needed to find any errors in installation
    for command in commands:
        with Popen(command, stdout=PIPE, bufsize=1, universal_newlines=True) as process:
            for line in process.stdout:
                print(line, end="")

        if process.returncode != 0:
            raise CalledProcessError(process.returncode, process.args)


def extract_zip(path, temp_dir, package):
    """
    Extracts zip file and moves it to temporary directory
    """

    # Extract zip file into directory
    # Moved automatically into temporary directory
    with ZipFile(path) as zip_file:
        for file in tqdm(zip_file.namelist(), total=len(zip_file.namelist())):
            zip_file.extract(file, temp_dir)

    # Extract file prefix
    filename = basename(path)
    zip_name, _ = splitext(filename)

    # Switch to directory and Check that setup.py exists
    # Running setup.py from a path for some reason doesn't work
    chdir(join(temp_dir, zip_name))
    if not exists(SETUP_SCRIPT):
        print("%s for package %s does not exist" % (SETUP_SCRIPT, package))
        raise SystemExit


def extract_tarball(path, temp_dir, package):
    """
    Extracts tar file and moves it to temporary directory.
    """

    # Extract tar file into directory
    # Will store directory into current working directory
    with tarfile.open(path) as tar:
        for member in tqdm(tar.getmembers(), total=len(tar.getmembers())):
            tar.extract(member)

    # Extract file prefix
    tar_name, _, _ = basename(tar.name).rsplit(".", 2)

    # Move directory into temporary directory
    # Avoids flooding current working directory with too many folders
    move(join(ROOT_PATH, tar_name), temp_dir)

    # Switch to directory and Check that setup.py exists
    # Running setup.py from a path for some reason doesn't work
    chdir(join(temp_dir, tar_name))
    if not exists(SETUP_SCRIPT):
        print("%s for package %s does not exist" % (SETUP_SCRIPT, package))
        raise SystemExit


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

        # If one package specified
        if args.package:
            url = ROOT_URL + args.package + FILE_LOCATION
            extract_html(args.package, url, temp_dir)

        # Otherwise, a file must have been supplied
        else:
            packages = parse_file(args.requirements)
            for package in packages:
                url = ROOT_URL + package + FILE_LOCATION
                extract_html(package, url, temp_dir)


if __name__ == "__main__":
    main()
