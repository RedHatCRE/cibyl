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
import unittest

from cibyl.models.ci.job import Job
from cibyl.models.ci.pipeline import Pipeline


# pylint: disable=no-member
class TestPipeline(unittest.TestCase):
    """Test Pipeline CI model."""

    def setUp(self):
        self.pipeline_name = 'test-pipeline'
        self.pipeline = Pipeline(name=self.pipeline_name)
        self.second_pipeline = Pipeline(name=self.pipeline_name)

    def test_pipeline_name(self):
        """Test new Pipeline name attribute."""
        self.assertTrue(
            hasattr(self.pipeline, 'name'), msg="Pipeline lacks name")

        self.assertEqual(
            self.pipeline.name.value, self.pipeline_name,
            msg=f"Pipeline name is {self.pipeline.name.value}. \
Should be {self.pipeline_name}")

    def test_pipelines_comparison(self):
        """Test new Pipeline instances comparison."""
        self.assertEqual(
            self.pipeline, self.second_pipeline,
            msg=f"Pipelines {self.pipeline.name.value} and \
{self.second_pipeline.name.value} are not equal")

    def test_pipelines_comparison_other_types(self):
        """Test new Pipeline instances comparison."""
        self.assertNotEqual(
            self.pipeline, "test",
            msg=f"Pipeline {self.pipeline.name.value} should be different \
from str")

    def test_pipeline_str(self):
        """Test Pipeline __str__ method."""
        self.assertIn('Pipeline: ', str(self.pipeline))
        self.assertIn('Pipeline: ', str(self.second_pipeline))
        self.assertIn(self.pipeline.name.value, str(self.pipeline))
        self.assertIn(self.second_pipeline.name.value,
                      str(self.second_pipeline))

    def test_pipeline_add_job(self):
        """Test Pipeline add_jobs method."""
        job1 = Job("name")
        self.pipeline.add_job(job1)
        job2 = Job("name")
        self.pipeline.add_job(job2)
        self.assertEqual(len(self.pipeline.jobs), 1)

    def test_pipeline_merge(self):
        """Test Pipeline merge method."""
        job1 = Job("name")
        self.pipeline.add_job(job1)
        job2 = Job("name")
        self.second_pipeline.add_job(job2)
        self.pipeline.merge(self.second_pipeline)
        self.assertEqual(len(self.pipeline.jobs), 1)
