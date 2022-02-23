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


class TestJob(unittest.TestCase):
    """Testing Job CI model"""

    def setUp(self):
        self.job_name = 'test-job'
        self.job_status = 'FAILURE'
        self.job_url = 'http://ci_system/test-job'
        self.job = Job(name=self.job_name)
        self.second_job = Job(name=self.job_name, status=self.job_status)

    def test_job_name(self):
        """Testing new Job name attribute"""
        self.assertTrue(
            hasattr(self.job, 'name'), msg="Job lacks name attribute")

        self.assertEqual(
            self.job.name.value, self.job_name,
            msg="Job name is {}. Should be {}".format(
                self.job.name.value, self.job_name))

    def test_job_status(self):
        """Testing new Job status attribute"""
        self.assertTrue(
            hasattr(self.job, 'status'), msg="Job lacks status attribute")

        self.assertEqual(
            self.job.status.value, None,
            msg="Job default status is {}. Should be {}".format(
                self.job.status.value, None))

        self.assertEqual(
            self.second_job.status.value, self.job_status,
            msg="Job default status is {}. Should be {}".format(
                self.second_job.status.value, self.job_status))

        self.job.status.value = self.job_status

        self.assertEqual(
            self.job.status.value, self.job_status,
            msg="New job status is {}. Should be {}".format(
                self.job.status.value, self.job_status))

    def test_job_url(self):
        """Testing new Job url attribute"""
        self.assertTrue(
            hasattr(self.job, 'url'), msg="Job lacks url attribute")

        self.assertEqual(
            self.job.url.value, None,
            msg="Job default url is {}. Should be {}".format(
                self.job.url.value, None))

        self.job.url.value = self.job_url

        self.assertEqual(
            self.job.url.value, self.job_url,
            msg="New job url is {}. Should be {}".format(
                self.job.url.value, self.job_url))

    def test_jobs_comparison(self):
        """Testing new Job instances comparison."""
        self.assertEqual(
            self.job, self.second_job,
            msg="Jobs {} and {} are not equal".format(
                self.job.name.value, self.second_job.name.value))

    def test_job_str(self):
        """Testing Job __str__ method"""
        self.assertEqual(str(self.job), 'Job: {}'.format(self.job.name.value))

        self.assertEqual(str(self.second_job), 'Job: {}\n  Status: {}'.format(
            self.job_name, self.job_status))

        self.second_job.url.value = self.job_url

        self.assertEqual(str(self.second_job),
                         'Job: {}\n  Status: {}\n  URL: {}'.format(
                             self.job_name, self.job_status, self.job_url))
