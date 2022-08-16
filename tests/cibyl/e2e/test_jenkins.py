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
import sys

from cibyl.cli.main import main
from cibyl.utils.colors import Colors
from cibyl.utils.strings import IndentedTextBuilder
from tests.cibyl.e2e.containers.jenkins import JenkinsContainer
from tests.cibyl.e2e.fixtures import EndToEndTest


class TestJenkins(EndToEndTest):
    """Tests queries regarding the Jenkins source.
    """

    def test_get_jobs(self):
        """Checks that jobs are retrieved with the "--jobs" flag.
        """
        with JenkinsContainer() as jenkins:
            jenkins.add_job('test_1')
            jenkins.add_job('test_2')

            sys.argv = [
                'cibyl',
                '--config', 'tests/cibyl/e2e/data/configs/jenkins.yaml',
                '-f', 'text',
                '-vv', 'query',
                '--jobs'
            ]

            main()

            self.assertIn('Total jobs found in query: 2', self.stdout)

    def test_jobs_are_alphabetically_ordered(self):
        """Checks that jobs are printed following an alphabetical order.
        """
        with JenkinsContainer() as jenkins:
            jenkins.add_job('this-is-a-job')
            jenkins.add_job('a-job')
            jenkins.add_job('job-x')

            sys.argv = [
                'cibyl',
                '--config', 'tests/cibyl/e2e/data/configs/jenkins.yaml',
                '-f', 'text', 'query',
                '--jobs'
            ]

            main()

            expected = IndentedTextBuilder()
            expected.add('Job: a-job', 2)
            expected.add('Job: job-x', 2)
            expected.add('Job: this-is-a-job', 2)
            expected.add('Total jobs found in query: 3', 2)

            self.assertIn(expected.build(), self.stdout)


class TestJenkinsCore(EndToEndTest):
    """Tests queries regarding the Jenkins core source.
    """
    jenkins = JenkinsContainer(compose_file='docker-compose_jenkins_core.yml')

    @classmethod
    def setUpClass(cls):
        cls.jenkins.start()

    @classmethod
    def tearDownClass(cls):
        cls.jenkins.stop()

    def test_get_tests(self):
        """Checks that jobs are retrieved with the "--tests" flag.
        """
        sys.argv = [
            'cibyl',
            '--config', 'tests/cibyl/e2e/data/configs/jenkins.yaml',
            '-f', 'text', 'query', '--tests', '--last-build'
        ]

        main()

        expected = IndentedTextBuilder()
        expected.add('Job: test_1', 2)
        expected.add('Build: 2', 3)
        expected.add('Status: UNSTABLE', 4)
        expected.add('Test: test_case1', 4)
        expected.add('Result: FAILED', 5)
        expected.add('Class name: class_test_1', 5)
        expected.add('Test: test_case2', 4)
        expected.add('Result: PASSED', 5)
        expected.add('Class name: class_test_1', 5)
        expected.add('Test: test_case3', 4)
        expected.add('Result: SKIPPED', 5)
        expected.add('Class name: class_test_1', 5)
        expected.add('Job: test_2', 2)
        expected.add('Build: 2', 3)
        expected.add('Status: SUCCESS', 4)
        expected.add('Test: test_case1', 4)
        expected.add('Result: FAILED', 5)
        expected.add('Class name: class_test_1', 5)
        expected.add('Test: test_case2', 4)
        expected.add('Result: PASSED', 5)
        expected.add('Class name: class_test_1', 5)
        expected.add('Test: test_case3', 4)
        expected.add('Result: SKIPPED', 5)
        expected.add('Class name: class_test_1', 5)
        expected.add('Job: test_3', 2)
        expected.add('Build: 1', 3)
        expected.add('Status: FAILURE', 4)
        expected.add('No tests in query.', 4)
        expected.add('Job: test_4', 2)
        expected.add('No builds in query.', 3)
        expected.add('Total jobs found in query: 4', 2)

        self.assertIn(expected.build(), self.stdout)

    def test_get_tests_verbose_output(self):
        """Checks that jobs are retrieved with the "--tests" flag and verbose
        output.
        """
        sys.argv = [
            'cibyl',
            '--config', 'tests/cibyl/e2e/data/configs/jenkins.yaml',
            '-f', 'text',  '-vv', 'query', '--tests', '--last-build'
        ]

        main()

        expected = IndentedTextBuilder()
        expected.add('Job: test_1', 2)
        expected.add('URL: http://localhost:8080/job/test_1/', 3)
        expected.add('Build: 2', 3)
        expected.add('Status: UNSTABLE', 4)
        expected.add('Test: test_case1', 4)
        expected.add('Result: FAILED', 5)
        expected.add('Class name: class_test_1', 5)
        expected.add('Duration: 0.01m', 5)
        expected.add('Test: test_case2', 4)
        expected.add('Result: PASSED', 5)
        expected.add('Class name: class_test_1', 5)
        expected.add('Duration: 0.00m', 5)
        expected.add('Test: test_case3', 4)
        expected.add('Result: SKIPPED', 5)
        expected.add('Class name: class_test_1', 5)
        expected.add('Duration: 0.08m', 5)
        expected.add('Job: test_2', 2)
        expected.add('URL: http://localhost:8080/job/test_2/', 3)
        expected.add('Build: 2', 3)
        expected.add('Status: SUCCESS', 4)
        expected.add('Test: test_case1', 4)
        expected.add('Result: FAILED', 5)
        expected.add('Class name: class_test_1', 5)
        expected.add('Duration: 0.01m', 5)
        expected.add('Test: test_case2', 4)
        expected.add('Result: PASSED', 5)
        expected.add('Class name: class_test_1', 5)
        expected.add('Duration: 0.00m', 5)
        expected.add('Test: test_case3', 4)
        expected.add('Result: SKIPPED', 5)
        expected.add('Class name: class_test_1', 5)
        expected.add('Duration: 0.08m', 5)
        expected.add('Job: test_3', 2)
        expected.add('URL: http://localhost:8080/job/test_3/', 3)
        expected.add('Build: 1', 3)
        expected.add('Status: FAILURE', 4)
        expected.add('No tests in query.', 4)
        expected.add('Job: test_4', 2)
        expected.add('URL: http://localhost:8080/job/test_4/', 3)
        expected.add('No builds in query.', 3)
        expected.add('Total jobs found in query: 4', 2)

        self.assertIn(expected.build(), self.stdout)

    def test_get_builds(self):
        """Checks that jobs are retrieved with the "--last-build" flag.
        """
        sys.argv = [
            'cibyl',
            '--config', 'tests/cibyl/e2e/data/configs/jenkins.yaml',
            '-f', 'text', 'query', '--last-build'
        ]

        main()
        expected = IndentedTextBuilder()
        expected.add('Job: test_1', 2)
        expected.add('Build: 2', 3)
        expected.add('Status: UNSTABLE', 4)
        expected.add('Job: test_2', 2)
        expected.add('Build: 2', 3)
        expected.add('Status: SUCCESS', 4)
        expected.add('Job: test_3', 2)
        expected.add('Build: 1', 3)
        expected.add('Status: FAILURE', 4)
        expected.add('Job: test_4', 2)
        expected.add('No builds in query.', 3)
        expected.add('Total jobs found in query: 4', 2)

        self.assertIn(expected.build(), self.stdout)

    def test_get_all_builds(self):
        """Checks that all builds for all jobs are retrieved with the "--builds" flag.
        """
        sys.argv = [
            'cibyl',
            '--config', 'tests/cibyl/e2e/data/configs/jenkins.yaml',
            '-f', 'text', 'query', '--builds'
        ]

        main()
        expected = IndentedTextBuilder()
        expected.add('Job: test_1', 2)
        expected.add('Build: 2', 3)
        expected.add('Status: UNSTABLE', 4)
        expected.add('Build: 1', 3)
        expected.add('Status: FAILURE', 4)
        expected.add('Job: test_2', 2)
        expected.add('Build: 2', 3)
        expected.add('Status: SUCCESS', 4)
        expected.add('Build: 1', 3)
        expected.add('Status: SUCCESS', 4)
        expected.add('Job: test_3', 2)
        expected.add('Build: 1', 3)
        expected.add('Status: FAILURE', 4)
        expected.add('Job: test_4', 2)
        expected.add('No builds in query.', 3)
        expected.add('Total jobs found in query: 4', 2)

        self.assertIn(expected.build(), self.stdout)

    def test_get_builds_by_build_id(self):
        """Checks that builds are filtered with the "--builds" flag and
        filtered by build id.
        """
        sys.argv = [
            'cibyl',
            '--config', 'tests/cibyl/e2e/data/configs/jenkins.yaml',
            '-f', 'text', 'query', '--builds', '2'
        ]

        main()
        expected = IndentedTextBuilder()
        expected.add('Job: test_1', 2)
        expected.add('Build: 2', 3)
        expected.add('Status: UNSTABLE', 4)
        expected.add('Job: test_2', 2)
        expected.add('Build: 2', 3)
        expected.add('Status: SUCCESS', 4)
        expected.add('Total jobs found in query: 2', 2)

        self.assertIn(expected.build(), self.stdout)

    def test_get_tests_with_build_id(self):
        """Checks that jobs are retrieved with the "--tests" flag and filtering
        by build id.
        """
        sys.argv = [
            'cibyl',
            '--config', 'tests/cibyl/e2e/data/configs/jenkins.yaml',
            '-f', 'text', 'query', '--tests', '--builds', '1'
        ]

        main()

        expected = IndentedTextBuilder()
        expected.add('Job: test_1', 2)
        expected.add('Build: 1', 3)
        expected.add('Status: FAILURE', 4)
        expected.add('No tests in query.', 4)
        expected.add('Job: test_2', 2)
        expected.add('Build: 1', 3)
        expected.add('Status: SUCCESS', 4)
        expected.add('No tests in query.', 4)
        expected.add('Job: test_3', 2)
        expected.add('Build: 1', 3)
        expected.add('Status: FAILURE', 4)
        expected.add('No tests in query.', 4)
        expected.add('Total jobs found in query: 3', 2)

        self.assertIn(expected.build(), self.stdout)

    def test_filter_build_id_test_result(self):
        """Checks that jobs are filtered with the "--builds" and
        "--test-result" flag.
        """
        sys.argv = [
            'cibyl',
            '--config', 'tests/cibyl/e2e/data/configs/jenkins.yaml',
            '-f', 'text', 'query', '--test-result', 'passed', '--builds', '2'
        ]

        main()

        expected = IndentedTextBuilder()
        expected.add('Job: test_1', 2)
        expected.add('Build: 2', 3)
        expected.add('Status: UNSTABLE', 4)
        expected.add('Test: test_case2', 4)
        expected.add('Result: PASSED', 5)
        expected.add('Class name: class_test_1', 5)
        expected.add('Job: test_2', 2)
        expected.add('Build: 2', 3)
        expected.add('Status: SUCCESS', 4)
        expected.add('Test: test_case2', 4)
        expected.add('Result: PASSED', 5)
        expected.add('Class name: class_test_1', 5)
        expected.add('Total jobs found in query: 2', 2)

        self.assertIn(expected.build(), self.stdout)

    def test_filter_build_id_test_name(self):
        """Checks that jobs are filtered with the "--builds" and
        "--tests" flag.
        """
        sys.argv = [
            'cibyl',
            '--config', 'tests/cibyl/e2e/data/configs/jenkins.yaml',
            '-f', 'text', 'query', '--tests', 'case2', '--builds', '2'
        ]

        main()

        expected = IndentedTextBuilder()
        expected.add('Job: test_1', 2)
        expected.add('Build: 2', 3)
        expected.add('Status: UNSTABLE', 4)
        expected.add('Test: test_case2', 4)
        expected.add('Result: PASSED', 5)
        expected.add('Class name: class_test_1', 5)
        expected.add('Job: test_2', 2)
        expected.add('Build: 2', 3)
        expected.add('Status: SUCCESS', 4)
        expected.add('Test: test_case2', 4)
        expected.add('Result: PASSED', 5)
        expected.add('Class name: class_test_1', 5)
        expected.add('Total jobs found in query: 2', 2)

        self.assertIn(expected.build(), self.stdout)

    def test_filter_build_id_test_duration(self):
        """Checks that jobs are filtered with the "--builds" and
        "--test-duration" flag.
        """
        sys.argv = [
            'cibyl',
            '--config', 'tests/cibyl/e2e/data/configs/jenkins.yaml',
            '-f', 'text', 'query', '--test-duration', '>3',  '<10',
            '--builds', '2'
        ]

        main()

        expected = IndentedTextBuilder()
        expected.add('Job: test_1', 2)
        expected.add('Build: 2', 3)
        expected.add('Status: UNSTABLE', 4)
        expected.add('Test: test_case3', 4)
        expected.add('Result: SKIPPED', 5)
        expected.add('Class name: class_test_1', 5)
        expected.add('Job: test_2', 2)
        expected.add('Build: 2', 3)
        expected.add('Status: SUCCESS', 4)
        expected.add('Test: test_case3', 4)
        expected.add('Result: SKIPPED', 5)
        expected.add('Class name: class_test_1', 5)
        expected.add('Total jobs found in query: 2', 2)

        self.assertIn(expected.build(), self.stdout)


class TestFeatures(EndToEndTest):
    """Tests related to the --features argument.
    """

    def test_status_bar_text_is_removed(self):
        """Checks that the status bar is removed before the output is printed.
        """
        with JenkinsContainer():
            sys.argv = [
                'cibyl',
                '--config',
                'tests/cibyl/e2e/data/configs/jenkins/with-openstack.yaml',
                '-f', 'text', 'features', 'IPv4'
            ]

            main()

            # Check that the eraser is printed
            status_bar_text = Colors.green(
                'Fetching features (osp_jenkins) ' + (' ' * 4)
            )

            self.assertIn(
                '\r' + (' ' * len(status_bar_text)) + '\r',
                self.stdout
            )
