import os
import unittest
import urllib.request

from eu.softfire.tub.core.CoreManagers import CsarManager
from eu.softfire.tub.utils.utils import get_logger

logger = get_logger("eu.softfire.tests")


class MyTestCase(unittest.TestCase):
    def test_csar(self):
        tempfile = "/tmp/example.csar"
        urllib.request.urlretrieve("http://docs.softfire.eu/etc/example.csar", tempfile)
        tpl = CsarManager(tempfile).get_main_definition()
        os.remove(tempfile)
        self.assertIsNotNone(tpl)
        self.assertFalse(os.path.exists(tempfile))


if __name__ == '__main__':
    unittest.main()
