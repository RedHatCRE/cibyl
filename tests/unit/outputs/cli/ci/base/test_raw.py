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
from cibyl.models.ci.base.environment import Environment
from cibyl.models.ci.base.system import JobsSystem
from cibyl.models.ci.base.test import Test
from cibyl.models.ci.zuul.job import Job
from cibyl.outputs.cli.ci.base.raw import RawBasePrinter


class TestCIRawPrinter(TestCase):
    """Tests for :class:`CIRawPrinter`.
    """

    def test_str_environment(self):
        """Testing printing of an environment.
        """
        name = "test_env"
        env = Environment(name)

        printer = RawBasePrinter()

        self.assertIn("Environment: ", printer.print_environment(env))
        self.assertIn(name, printer.print_environment(env))

    def test_print_build(self):
        """Testing printing of a standard build.
        """
        build_id = 'test-build'
        build_status = 'FAILURE'

        build1 = Build(build_id=build_id)
        build2 = Build(build_id=build_id)

        printer = RawBasePrinter()

        self.assertIn('Build: ', printer.print_build(build1))
        self.assertIn(build_id, printer.print_build(build1))
        self.assertIn('Build: ', printer.print_build(build2))

        build2.status.value = build_status

        self.assertIn('Build: ', printer.print_build(build2))
        self.assertIn('Status: ', printer.print_build(build2))
        self.assertIn(build_id, printer.print_build(build2))

    def test_print_build_complete(self):
        """Testing printing of a complete build.
        """
        build_id = 'test-build'
        test = Test("test_name", "failure")

        build = Build(build_id=build_id)
        build.add_test(test)

        build.status.value = "SUCCESS"
        build.duration.value = 60000

        printer = RawBasePrinter(verbosity=2)
        result = printer.print_build(build)

        self.assertIn('Build: ', result)
        self.assertIn(build_id, result)
        self.assertIn('Duration:', result)
        self.assertIn('1.00m', result)
        self.assertIn('Test:', result)

    def test_print_build_all_status(self):
        """Testing all possible statuses of a build.
        """
        statuses = ["SUCCESS", "FAILURE", "UNSTABLE"]
        for status in statuses:
            build = Build(build_id='build')
            build.status.value = status

            printer = RawBasePrinter()
            result = printer.print_build(build)

            self.assertIn('Status: ', result)
            self.assertIn(status, result)

    def test_print_job(self):
        """Testing printing of a job.
        """
        job_name = 'test-job'
        job_url = 'http://ci_system/test-job'

        job1 = Job(name=job_name, url=job_url)
        job2 = Job(name=job_name, url=job_url)

        printer = RawBasePrinter()

        self.assertIn('Job: ', printer.print_job(job1))
        self.assertIn('Job: ', printer.print_job(job2))
        self.assertIn(job1.name.value, printer.print_job(job1))
        self.assertIn(job_name, printer.print_job(job2))

        job2.url.value = job_url

        self.assertIn('Job: ', printer.print_job(job2))
        self.assertIn(job_name, printer.print_job(job2))

    def test_print_test(self):
        """Test printing of a test.
        """
        name = 'test-test'
        test_result = 'FAILURE'
        class_name = 'unit'
        duration = 25

        test1 = Test(name=name)
        test2 = Test(name=name)

        printer = RawBasePrinter(verbosity=2)

        self.assertIn('Test: ', printer.print_test(test1))
        self.assertIn(name, printer.print_test(test1))
        self.assertIn('Test: ', printer.print_test(test2))

        test2.result.value = test_result
        test2.duration.value = duration
        test2.class_name.value = class_name

        result2 = printer.print_test(test2)

        self.assertIn('Test: ', result2)
        self.assertIn(name, result2)
        self.assertIn('Result: ', result2)
        self.assertIn(test_result, result2)
        self.assertIn('Class name: ', result2)
        self.assertIn(class_name, result2)
        self.assertIn('Duration:', result2)
        self.assertIn('0.00m', result2)

    def test_print_test_all_results(self):
        """Test all possible results of a test.
        """
        results = ["SUCCESS", "FAILURE", "UNSTABLE", "SKIPPED"]

        printer = RawBasePrinter(verbosity=2)

        for result in results:
            test = Test(name='test')
            test.result.value = result

            result = printer.print_test(test)

            self.assertIn('Result: ', result)
            self.assertIn(result, result)

    def test_system_str_jobs(self):
        """Test system str for a system with jobs and builds."""
        system = JobsSystem("test", "test_type")
        build = Build("1", "SUCCESS")
        job = Job("test_job", 'test_url')
        job.add_build(build)
        system.add_job(job)
        system.register_query()

        printer = RawBasePrinter(verbosity=0)

        output = printer.print_system(system)
        expected = """System: test
    Job: test_job
      Build: 1
        Status: SUCCESS
    Total jobs found in query: 1"""
        self.assertIn(output, expected)
