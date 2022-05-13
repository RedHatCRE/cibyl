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

from cibyl.models.ci.base.test import Test


class TestTest(unittest.TestCase):
    """Test Test CI model."""

    def setUp(self):
        self.name = 'test-test'
        self.test_result = 'FAILURE'
        self.class_name = 'unit'
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

    def test_test_result(self):
        """Test new Test result attribute."""
        self.assertTrue(
            hasattr(self.test, 'result'), msg="Test lacks result attribute")

        self.assertEqual(
            self.test.result.value, None,
            msg=f"Test default result is {self.test.result.value}. \
Should be None")

        self.assertEqual(
            self.second_test.result.value, None,
            msg=f"Test default result is {self.second_test.result.value}.\
 Should be None")

        self.test.result.value = self.test_result

        self.assertEqual(
            self.test.result.value, self.test_result,
            msg="New test result is {self.test.result.value}. \
Should be {self.test_result}")

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

    def test_test_merge(self):
        """Test Test merge method."""
        self.test.result.value = "SUCCESS"
        self.test.duration.value = self.duration
        self.second_test.merge(self.test)
        self.assertEqual(self.second_test.result.value, "SUCCESS")
        self.assertEqual(self.second_test.duration.value, 25)
