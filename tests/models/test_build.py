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
        self.build_id = 'test-build'
        self.build_status = 'FAILURE'
        self.build = Build(build_id=self.build_id)
        self.second_build = Build(build_id=self.build_id)

    def test_build_id(self):
        """Testing new Build id attribute"""
        self.assertTrue(
            hasattr(self.build, 'build_id'),
            msg="Build lacks build_id attribute")

        self.assertEqual(
            self.build.build_id.value, self.build_id,
            msg=f"Build id is {self.build.build_id.value}. \
Should be {self.build_id}")

    def test_build_status(self):
        """Testing new Build status attribute"""
        self.assertTrue(
            hasattr(self.build, 'status'), msg="Build lacks status attribute")

        self.assertEqual(
            self.build.status.value, None,
            msg=f"Build default status is {self.build.status.value}. \
Should be None")

        self.assertEqual(
            self.second_build.status.value, None,
            msg=f"Build default status is {self.second_build.status.value}.\
 Should be None")

        self.build.status.value = self.build_status

        self.assertEqual(
            self.build.status.value, self.build_status,
            msg="New build status is {self.build.status.value}. \
Should be {self.build_status}")

    def test_builds_comparison(self):
        """Testing new Build instances comparison."""
        self.assertEqual(
            self.build, self.second_build,
            msg=f"Builds {self.build.build_id.value} and \
{self.second_build.build_id.value} are not equal")

    def test_builds_comparison_other_types(self):
        """Testing new Build instances comparison."""
        self.assertNotEqual(
            self.build, "test",
            msg=f"Build {self.build.build_id.value} should be different from \
str")

    def test_build_str(self):
        """Testing Build __str__ method"""
        self.assertEqual(str(self.build), f'Build: {self.build_id}')

        self.assertEqual(
            str(self.second_build),
            f'Build: {self.build_id}')

        self.second_build.status.value = self.build_status

        self.assertEqual(
                str(self.second_build),
                f'Build: {self.build_id}\n  Status: {self.build_status}')
