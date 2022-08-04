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
