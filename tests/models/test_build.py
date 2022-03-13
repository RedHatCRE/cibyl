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

from cibyl.models.ci.build import Build


class TestBuild(unittest.TestCase):
    """Testing Build CI model"""

    def setUp(self):
        self.build_number = 'test-build'
        self.build_result = 'FAILURE'
        self.build = Build(number=self.build_number)
        self.second_build = Build(number=self.build_number)

    def test_build_number(self):
        """Testing new Build id attribute"""
        self.assertTrue(
            hasattr(self.build, 'number'),
            msg="Build lacks number attribute")

        self.assertEqual(
            self.build.number.value, self.build_number,
            msg=f"Build id is {self.build.number.value}. \
Should be {self.build_number}")

    def test_build_result(self):
        """Testing new Build result attribute"""
        self.assertTrue(
            hasattr(self.build, 'result'), msg="Build lacks result attribute")

        self.assertEqual(
            self.build.result.value, None,
            msg=f"Build default result is {self.build.result.value}. \
Should be None")

        self.assertEqual(
            self.second_build.result.value, None,
            msg=f"Build default result is {self.second_build.result.value}.\
 Should be None")

        self.build.result.value = self.build_result

        self.assertEqual(
            self.build.result.value, self.build_result,
            msg="New build result is {self.build.result.value}. \
Should be {self.build_result}")

    def test_builds_comparison(self):
        """Testing new Build instances comparison."""
        self.assertEqual(
            self.build, self.second_build,
            msg=f"Builds {self.build.number.value} and \
{self.second_build.number.value} are not equal")

    def test_builds_comparison_other_types(self):
        """Testing new Build instances comparison."""
        self.assertNotEqual(
            self.build, "test",
            msg=f"Build {self.build.number.value} should be different from \
str")

    def test_build_str(self):
        """Testing Build __str__ method"""
        self.assertEqual(str(self.build), f'Build: {self.build_number}')

        self.assertEqual(
            str(self.second_build),
            f'Build: {self.build_number}')

        self.second_build.result.value = self.build_result

        self.assertEqual(
                str(self.second_build),
                f'Build: {self.build_number}\n  result: {self.build_result}')
