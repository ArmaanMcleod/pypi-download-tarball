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

    def test_download_file(self):
        link = "https://files.pythonhosted.org/packages/40/35/298c36d839547b50822985a2cf0611b3b978a5ab7a5af5562b8ebe3e1369/requests-2.20.1.tar.gz"
        filename = basename(link)
        response = get(link)
        path = join(getcwd(), filename)

        downloaded_file = download.run_download(
            filename=filename, response=response, path=path
        )
        self.assertTrue(isfile(downloaded_file))

        remove(path)

    def test_process(self):
        self.assertEqual(download.run_process(['ls']), 0)

if __name__ == "__main__":
    unittest.main()
