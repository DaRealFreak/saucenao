#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
import unittest

from saucenao import __version__ as saucenao_version


class TestVersion(unittest.TestCase):
    """Test the version information for Python PEP standard"""

    def test_version_format(self):
        """Test the version number for a PyPi valid format according to PEP 440
        https://www.python.org/dev/peps/pep-0440/

        :return:
        """
        # ToDo: check all requirements
        self.assertEqual(bool(re.match('\d+.\d+', saucenao_version.__version__)), True)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestVersion)
    unittest.TextTestRunner(verbosity=2).run(suite)
