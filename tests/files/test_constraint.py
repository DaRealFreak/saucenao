#!/usr/bin/python
# -*- coding: utf-8 -*-
import unittest

from saucenao.files.constraint import Constraint


class TestConstraint(unittest.TestCase):
    """
    test cases for the constraints in the files submodule
    """

    def test_constraint(self):
        """Test the initializing function of Constraint

        :return:
        """
        constraint = Constraint(value='Value', cmp_func=self)
        self.assertEqual(constraint.value, 'Value')
        self.assertEqual(constraint.cmp_func, self)

    def test_value_bigger(self):
        """Test compare function cmp_value_bigger

        :return:
        """
        self.assertEqual(Constraint.cmp_value_bigger(1, 2), False)
        self.assertEqual(Constraint.cmp_value_bigger(2, 2), False)
        self.assertEqual(Constraint.cmp_value_bigger(2, 1), True)

    def test_value_bigger_or_equal(self):
        """Test compare function cmp_value_bigger

        :return:
        """
        self.assertEqual(Constraint.cmp_value_bigger_or_equal(1, 2), False)
        self.assertEqual(Constraint.cmp_value_bigger_or_equal(2, 2), True)
        self.assertEqual(Constraint.cmp_value_bigger_or_equal(2, 1), True)

    def test_value_smaller(self):
        """Test compare function cmp_value_bigger

        :return:
        """
        self.assertEqual(Constraint.cmp_value_smaller(1, 2), True)
        self.assertEqual(Constraint.cmp_value_smaller(2, 2), False)
        self.assertEqual(Constraint.cmp_value_smaller(2, 1), False)

    def test_value_smaller_or_equal(self):
        """Test compare function cmp_value_bigger

        :return:
        """
        self.assertEqual(Constraint.cmp_value_smaller_or_equal(1, 2), True)
        self.assertEqual(Constraint.cmp_value_smaller_or_equal(2, 2), True)
        self.assertEqual(Constraint.cmp_value_smaller_or_equal(2, 1), False)

    def test_value_equals(self):
        """Test compare function cmp_value_bigger

        :return:
        """
        self.assertEqual(Constraint.cmp_value_equals(1, 2), False)
        self.assertEqual(Constraint.cmp_value_equals(2, 2), True)
        self.assertEqual(Constraint.cmp_value_equals(2, 1), False)

    def test_value_not_equals(self):
        """Test compare function cmp_value_bigger

        :return:
        """
        self.assertEqual(Constraint.cmp_value_not_equals(1, 2), True)
        self.assertEqual(Constraint.cmp_value_not_equals(2, 2), False)
        self.assertEqual(Constraint.cmp_value_not_equals(2, 1), True)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestConstraint)
    unittest.TextTestRunner(verbosity=2).run(suite)
