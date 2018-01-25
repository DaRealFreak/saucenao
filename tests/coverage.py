#!/usr/local/bin/python
# coding: utf-8
import unittest

from tests.files import TestConstraint, TestFileHandler, TestFilesFilter

for test_case in (TestConstraint, TestFileHandler, TestFilesFilter):
    suite = unittest.TestLoader().loadTestsFromTestCase(test_case)
    unittest.TextTestRunner(verbosity=2).run(suite)
