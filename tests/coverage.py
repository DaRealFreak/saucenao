#!/usr/local/bin/python
# coding: utf-8
import unittest

from tests.files import __all__

for test_case in __all__:
    suite = unittest.TestLoader().loadTestsFromTestCase(test_case)
    unittest.TextTestRunner(verbosity=2).run(suite)
