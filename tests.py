import unittest

from os.path import basename
from os.path import isfile
from os.path import join

import download

from requests import get

from os import remove
from os import getcwd


class TestDownloads(unittest.TestCase):
    def test_parse_file(self):
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
        filename = basename(link)
        response = get(link)
        path = join(getcwd(), filename)

        downloaded_file = download.run_download(
            filename=filename, response=response, path=path
        )

        return downloaded_file

    def test_download_file(self):
        path = self.download_package(
            link="https://files.pythonhosted.org/packages/40/35/298c36d839547b50822985a2cf0611b3b978a5ab7a5af5562b8ebe3e1369/requests-2.20.1.tar.gz"
        )
        self.assertTrue(isfile(path))
        remove(path)

        path = self.download_package(
            link="https://files.pythonhosted.org/packages/2d/80/1809de155bad674b494248bcfca0e49eb4c5d8bee58f26fe7a0dd45029e2/numpy-1.15.4.zip"
        )
        self.assertTrue(isfile(path))
        remove(path)

    def test_process(self):
        self.assertEqual(download.run_process(["ls"]), 0)
        self.assertEqual(download.run_process(["ls", "-la"]), 0)
        self.assertRaises(FileNotFoundError, lambda: download.run_process(["blah"]))


if __name__ == "__main__":
    unittest.main()
