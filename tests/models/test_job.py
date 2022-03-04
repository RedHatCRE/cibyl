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

from cibyl.models.ci.build import Build
from cibyl.models.ci.job import Job


# pylint: disable=no-member
class TestJob(unittest.TestCase):
    """Testing Job CI model"""

    def setUp(self):
        self.job_name = 'test-job'
        self.job_status = 'FAILURE'
        self.job_url = 'http://ci_system/test-job'
        self.builds = [Build("1")]
        self.job = Job(name=self.job_name)
        self.second_job = Job(name=self.job_name)

    def test_job_name(self):
        """Testing new Job name attribute"""
        self.assertTrue(
            hasattr(self.job, 'name'), msg="Job lacks name attribute")

        self.assertEqual(
            self.job.name.value, self.job_name,
            msg=f"Job name is {self.job.name.value}. \
Should be {self.job_name}")

    def test_job_builds(self):
        """Testing new Job builds attribute"""
        self.assertTrue(
            hasattr(self.job, 'builds'), msg="Job lacks builds attribute")

        self.assertEqual(
            self.job.builds.value, [],
            msg=f"Job default builds is {self.job.builds.value}. \
Should be []")

        self.assertEqual(
            self.second_job.builds.value, [],
            msg="Job default builds are {self.second_job.builds.value}.\
 Should be []")

        self.job.builds.value = self.builds

        self.assertEqual(
            self.job.builds.value, self.builds,
            msg="New job builds are {self.job.builds.value}. \
Should be {self.builds}")

    def test_job_url(self):
        """Testing new Job url attribute"""
        self.assertTrue(
            hasattr(self.job, 'url'), msg="Job lacks url attribute")

        self.assertEqual(
            self.job.url.value, None,
            msg=f"Job default url is {self.job.url.value}. Should be {None}")

        self.job.url.value = self.job_url

        self.assertEqual(
            self.job.url.value, self.job_url,
            msg=f"New job url is {self.job.url.value}. \
Should be {self.job_url}")

    def test_jobs_comparison(self):
        """Testing new Job instances comparison."""
        self.assertEqual(
            self.job, self.second_job,
            msg=f"Jobs {self.job.name.value} and \
{self.second_job.name.value} are not equal")

    def test_jobs_comparison_other_type(self):
        """Testing new Job instances comparison."""
        self.assertNotEqual(
            self.job, "hello",
            msg=f"Job {self.job.name.value} should be different from str")

    def test_job_str(self):
        """Testing Job __str__ method."""
        self.assertEqual(str(self.job), f'Job: {self.job.name.value}')

        self.assertEqual(
            str(self.second_job),
            f'Job: {self.job_name}')

        self.second_job.url.value = self.job_url

        self.assertEqual(str(self.second_job),
                         f'Job: {self.job_name}\n  \
URL: {self.job_url}')

    def test_jobs_add_build(self):
        """Testing Job add_build method."""
        build2 = Build("2", "SUCCESS")
        self.job.add_build(build2)
        self.assertEqual(1, len(self.job.builds.value))
        self.assertEqual(build2, self.job.builds.value[0])
