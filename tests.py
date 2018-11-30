import unittest

import sys

from os.path import basename
from os.path import isfile
from os.path import join
from os.path import dirname

import download

from requests import get

from os import remove
from os import getcwd
from os import listdir
from os import walk

import tarfile

from tempfile import mkdtemp
from shutil import rmtree

from contextlib import closing
from zipfile import ZipFile

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.temp_folders = []

    def test_parse_file(self):
        logger.info("Running Test: test_parse_file")
        with open("test.txt", mode="w") as f:
            f.write("tqdm\n")
            f.write("twine\n")
            f.write("requests\n")
            f.write("beautifulsoup4\n")

        self.assertEqual(
            download.parse_file(filename="test.txt"),
            ["tqdm", "twine", "requests", "beautifulsoup4"],
        )
        self.assertEqual(
            download.parse_file(filename="requirements.txt"),
            ["tqdm", "twine", "requests", "beautifulsoup4"],
        )

        remove(f.name)

    def download_package(self, link):
        temp_dir = mkdtemp()
        self.temp_folders.append(temp_dir)
        filename = basename(link)
        response = get(link)
        path = join(temp_dir, filename)

        downloaded_file = download.run_download(
            filename=filename, response=response, path=path
        )

        return downloaded_file

    def test_download_file(self):
        logger.info("Running Test: test_download_file")
        downloaded_file = self.download_package(
            link="https://files.pythonhosted.org/packages/40/35/298c36d839547b50822985a2cf0611b3b978a5ab7a5af5562b8ebe3e1369/requests-2.20.1.tar.gz"
        )

        self.assertTrue(isfile(downloaded_file))

        downloaded_file = self.download_package(
            link="https://files.pythonhosted.org/packages/2d/80/1809de155bad674b494248bcfca0e49eb4c5d8bee58f26fe7a0dd45029e2/numpy-1.15.4.zip"
        )
        self.assertTrue(isfile(downloaded_file))

    def test_process(self):
        logger.info("Running Test: test_process")
        self.assertEqual(download.run_process(["ls"]), 0)
        self.assertEqual(download.run_process(["ls", "-la"]), 0)
        self.assertRaises(FileNotFoundError, lambda: download.run_process(["blah"]))

    def test_tar_extract(self):
        logger.info("Running Test: test_tar_extract")
        downloaded_file = self.download_package(
            link="https://files.pythonhosted.org/packages/40/35/298c36d839547b50822985a2cf0611b3b978a5ab7a5af5562b8ebe3e1369/requests-2.20.1.tar.gz"
        )

        with tarfile.open(downloaded_file) as archive:
            num_archived_files = sum(1 for member in archive if member.isreg())

        extracted_dir = download.extract_tarball(
            path=downloaded_file, directory=dirname(downloaded_file), package="requests"
        )
        num_extracted_files = len(
            [
                file
                for _, _, files in walk(extracted_dir, topdown=True)
                for file in files
            ]
        )

        self.assertEqual(num_archived_files, num_extracted_files)

    def test_zip_extract(self):
        logger.info("Running Test: test_zip_extract")
        downloaded_file = self.download_package(
            link="https://files.pythonhosted.org/packages/2d/80/1809de155bad674b494248bcfca0e49eb4c5d8bee58f26fe7a0dd45029e2/numpy-1.15.4.zip"
        )

        with ZipFile(file=downloaded_file) as zip_file:
            num_archived_files = len(zip_file.infolist())

        extracted_dir = download.extract_zip(
            path=downloaded_file, directory=dirname(downloaded_file), package="numpy"
        )
        num_extracted_files = len(
            [
                file
                for _, _, files in walk(extracted_dir, topdown=True)
                for file in files
            ]
        )

        self.assertEqual(num_archived_files, num_extracted_files)

    @classmethod
    def tearDown(self):
        for file in self.temp_folders:
            if isfile(file):
                rmtree(file)


if __name__ == "__main__":
    unittest.main()
