"""
# Copyright 2022 Red Hat
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
"""
# pylint: disable=no-member
import unittest

from cibyl.models.ci.test import Test


class TestTest(unittest.TestCase):
    """Test Test CI model."""

    def setUp(self):
        self.name = 'test-test'
        self.test_status = 'FAILURE'
        self.test = Test(name=self.name)
        self.second_test = Test(name=self.name)
        self.duration = 25

    def test_test_name(self):
        """Test new Test name attribute"""
        self.assertTrue(
            hasattr(self.test, 'name'),
            msg="Test lacks name attribute")

        self.assertEqual(
            self.test.name.value, self.name,
            msg=f"Test name is {self.test.name.value}. \
Should be {self.name}")

    def test_test_status(self):
        """Test new Test status attribute."""
        self.assertTrue(
            hasattr(self.test, 'status'), msg="Test lacks status attribute")

        self.assertEqual(
            self.test.status.value, None,
            msg=f"Test default status is {self.test.status.value}. \
Should be None")

        self.assertEqual(
            self.second_test.status.value, None,
            msg=f"Test default status is {self.second_test.status.value}.\
 Should be None")

        self.test.status.value = self.test_status

        self.assertEqual(
            self.test.status.value, self.test_status,
            msg="New test status is {self.test.status.value}. \
Should be {self.test_status}")

    def test_tests_comparison(self):
        """Test new Test instances comparison."""
        self.assertEqual(
            self.test, self.second_test,
            msg=f"Tests {self.test.name.value} and \
{self.second_test.name.value} are not equal")

    def test_tests_comparison_other_types(self):
        """Test new Test instances comparison."""
        self.assertNotEqual(
            self.test, "test",
            msg=f"Test {self.test.name.value} should be different from \
str")

    def test_test_str(self):
        """Test Test __str__ method."""
        self.assertIn('Test: ', str(self.test))
        self.assertIn(self.name, str(self.test))
        self.assertIn('Test: ', str(self.second_test))

        self.second_test.status.value = self.test_status
        self.second_test.duration.value = self.duration
        second_test_str = self.second_test.__str__(verbosity=2)

        self.assertIn('Test: ', second_test_str)
        self.assertIn('Status: ', second_test_str)
        self.assertIn(self.name, second_test_str)
        self.assertIn(self.test_status, second_test_str)
        self.assertIn('Duration:', second_test_str)
        self.assertIn('0.00m', second_test_str)

    def test_test_merge(self):
        """Test Test merge method."""
        self.test.status.value = "SUCCESS"
        self.test.duration.value = self.duration
        self.second_test.merge(self.test)
        self.assertEqual(self.second_test.status.value, "SUCCESS")
        self.assertEqual(self.second_test.duration.value, 25)

    def test_test_str_all_status(self):
        """Test Test str for various status strings."""
        statuses = ["SUCCESS", "FAILURE", "UNSTABLE", "SKIPPED"]
        for status in statuses:
            self.test.status.value = status
            test_str = str(self.test)
            self.assertIn('Status: ', test_str)
            self.assertIn(status, test_str)
