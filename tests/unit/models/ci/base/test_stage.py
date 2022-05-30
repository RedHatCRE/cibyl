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

from cibyl.models.ci.base.stage import Stage


class TestStage(unittest.TestCase):
    """Test Stage CI model."""

    def setUp(self):
        self.name = 'test-stage'
        self.stage_status = 'FAILURE'
        self.stage = Stage(name=self.name)
        self.second_stage = Stage(name=self.name)

    def test_name(self):
        """Test new Stage name attribute"""
        self.assertTrue(
            hasattr(self.stage, 'name'),
            msg="Stage lacks name attribute")

        self.assertEqual(
            self.stage.name.value, self.name,
            msg=f"Stage id is {self.stage.name.value}. \
Should be {self.name}")

    def test_stage_status(self):
        """Test new Stage status attribute."""
        self.assertTrue(
            hasattr(self.stage, 'status'), msg="Stage lacks status attribute")

        self.assertEqual(
            self.stage.status.value, None,
            msg=f"Stage default status is {self.stage.status.value}. \
Should be None")

        self.assertEqual(
            self.second_stage.status.value, None,
            msg=f"Stage default status is {self.second_stage.status.value}.\
 Should be None")

        self.stage.status.value = self.stage_status

        self.assertEqual(
            self.stage.status.value, self.stage_status,
            msg="New stage status is {self.stage.status.value}. \
Should be {self.stage_status}")

    def test_stages_comparison(self):
        """Test new Stage instances comparison."""
        self.assertEqual(
            self.stage, self.second_stage,
            msg=f"Stages {self.stage.name.value} and \
{self.second_stage.name.value} are not equal")

    def test_stages_comparison_other_types(self):
        """Test new Stage instances comparison."""
        self.assertNotEqual(
            self.stage, "test",
            msg=f"Stage {self.stage.name.value} should be different from \
str")

    def test_stage_merge(self):
        """Test Stage merge method."""
        self.stage.status.value = "SUCCESS"
        self.second_stage.merge(self.stage)
        self.assertEqual(self.second_stage.status.value, "SUCCESS")
