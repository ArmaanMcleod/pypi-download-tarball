import unittest

from sys import executable

from subprocess import run
from subprocess import DEVNULL

from importlib import import_module

import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TestDownloads(unittest.TestCase):
    def check_import(self, module):
        try:
            import_module(module)
            return True
        except ModuleNotFoundError:
            return False

    def test_download_xlrd(self):
        logger.debug("Running test: test_download_xlrd")
        run(
            [executable, "-m", "pip", "uninstall", "xlrd", "-y"],
            stdout=DEVNULL,
            stderr=DEVNULL,
        )
        self.assertFalse(self.check_import("xlrd"))
        run([executable, "download.py", "-p", "xlrd"], stdout=DEVNULL, stderr=DEVNULL)
        self.assertTrue(self.check_import("xlrd"))


if __name__ == "__main__":
    unittest.main()
