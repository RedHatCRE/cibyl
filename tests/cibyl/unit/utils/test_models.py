"""
#    Copyright 2022 Red Hat
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
from unittest import TestCase

from cibyl.models.ci.base.build import Build
from cibyl.models.ci.base.job import Job
from cibyl.models.ci.base.test import Test
from cibyl.utils.models import has_tests_job


class TestHastTestJob(TestCase):
    """Test has_tests_job function of utils.models module."""
    def test_has_tests_job_with_tests(self):
        """Checks that has_tests_job identifies that a job has tests.
        """
        test = Test(name="test")
        build = Build(build_id="1")
        build.add_test(test)
        job = Job(name="test")
        job.add_build(build)
        self.assertTrue(has_tests_job(job))

    def test_has_tests_job_with_build_no_tests(self):
        """Checks that has_tests_job identifies that a job has builds but no
        tests.
        """
        build = Build(build_id="1")
        job = Job(name="test")
        job.add_build(build)
        self.assertFalse(has_tests_job(job))

    def test_has_tests_job_with_no_build_no_tests(self):
        """Checks that has_tests_job identifies that a job has no builds and no
        tests.
        """
        job = Job(name="test")
        self.assertFalse(has_tests_job(job))
