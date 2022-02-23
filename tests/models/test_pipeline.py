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

from cibyl.models.ci.pipeline import Pipeline


class TestPipeline(unittest.TestCase):
    """Testing Pipeline CI model"""

    def setUp(self):
        self.pipeline_name = 'test-pipeline'
        self.pipeline = Pipeline(name=self.pipeline_name)
        self.second_pipeline = Pipeline(name=self.pipeline_name)

    def test_pipeline_name(self):
        """Testing new Pipeline name attribute"""
        self.assertTrue(
            hasattr(self.pipeline, 'name'), msg="Pipeline lacks name")

        self.assertEqual(
            self.pipeline.name.value, self.pipeline_name,
            msg="Pipeline name is {}. Should be {}".format(
                self.pipeline.name.value, self.pipeline_name))

    def test_pipelines_comparison(self):
        """Testing new Pipeline instances comparison."""
        self.assertEqual(
            self.pipeline, self.second_pipeline,
            msg="Pipelines {} and {} are not equal".format(
                self.pipeline.name.value, self.second_pipeline.name.value))

    def test_pipeline_str(self):
        """Testing Pipeline __str__ method"""
        self.assertEqual(str(self.pipeline),
                         f'Pipeline {self.pipeline.name.value}')

        self.assertEqual(str(self.second_pipeline),
                         f'Pipeline {self.second_pipeline.name.value}')
