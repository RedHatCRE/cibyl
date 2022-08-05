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
import logging
import sys
from io import StringIO
from tempfile import NamedTemporaryFile
from unittest import TestCase, skip
from unittest.mock import patch

from cibyl.cli.main import main
from cibyl.exceptions.jenkins import JenkinsError
from cibyl.models.attribute import AttributeDictValue
from cibyl.models.ci.base.build import Build
from cibyl.models.ci.base.job import Job
from cibyl.plugins.openstack.deployment import Deployment
from cibyl.plugins.openstack.network import Network
from cibyl.plugins.openstack.sources.jenkins import Jenkins as OSPJenkins
from cibyl.plugins.openstack.sources.zuul import Zuul as OSPZuul
from cibyl.sources.elasticsearch.api import ElasticSearch
from cibyl.sources.jenkins import Jenkins
from cibyl.sources.zuul.source import Zuul


class TestOrchestrator(TestCase):
    """Test the Orchestrator class."""

    @classmethod
    def setUpClass(cls):
        cls._original_stdout = sys.stdout
        # silence stdout and logging to avoid cluttering
        logging.disable(logging.CRITICAL)

    @classmethod
    def tearDownClass(cls):
        sys.stdout = cls._original_stdout

    def setUp(self):
        self._stdout = StringIO()
        sys.stdout = self._stdout

    @property
    def stdout(self):
        """
        :return: What the app wrote to stdout.
        :rtype: str
        """
        return self._stdout.getvalue()

    @patch.object(Jenkins, 'setup', return_value="")
    @patch('cibyl.orchestrator.get_source_instance_from_method')
    @patch('cibyl.orchestrator.source_information_from_method',
           return_value="")
    @patch.object(Jenkins, 'get_jobs', side_effect=JenkinsError)
    @patch.object(OSPJenkins, 'get_deployment', side_effect=JenkinsError)
    @patch('cibyl.plugins.get_classes_in', return_value=[OSPJenkins])
    def test_args_level(self, _get_classes_mock, jenkins_deployment,
                        jenkins_jobs, _, source_instance_mock,
                        jenkins_setup_mock):
        """Test that the args level is updated properly in run_query."""
        source_instance_mock.return_value = Jenkins(url="url")
        with NamedTemporaryFile() as config_file:
            config_file.write(b"environments:\n")
            config_file.write(b"  env:\n")
            config_file.write(b"    system:\n")
            config_file.write(b"      system_type: jenkins\n")
            config_file.write(b"      sources:\n")
            config_file.write(b"        jenkins:\n")
            config_file.write(b"          driver: jenkins\n")
            config_file.write(b"          url: url\n")
            config_file.seek(0)
            sys.argv = ['cibyl', '-p', 'openstack', '--config',
                        config_file.name, 'query', '--jobs', 'DFG-compute',
                        '--ip-version']

            main()
        jenkins_deployment.assert_called_once()
        jenkins_jobs.assert_not_called()
        jenkins_setup_mock.assert_called_once()

    @patch.object(Jenkins, 'setup', return_value="")
    @patch('cibyl.orchestrator.get_source_instance_from_method')
    @patch('cibyl.orchestrator.source_information_from_method',
           return_value="")
    @patch.object(Jenkins, 'get_builds')
    @patch.object(OSPJenkins, 'get_deployment')
    @patch('cibyl.plugins.get_classes_in', return_value=[OSPJenkins])
    def test_intersection_run_query(self, _get_classes_mock,
                                    jenkins_deployment, jenkins_builds,
                                    _, source_instance_mock,
                                    jenkins_setup_mock):
        """Test that the output of two source queries is combined properly
        in run_query."""
        source_instance_mock.return_value = Jenkins(url="url")
        builds = {"1": Build("1")}
        builds_out = {"job1": Job("job1", builds=builds), "job2": Job("job2")}
        network = Network(ip_version="4")
        deployment = Deployment("N/A", "N/A", {}, {}, network=network)
        deployment_out = {"job1": Job("job1", deployment=deployment),
                          "job3": Job("job3")}
        jenkins_builds.return_value = AttributeDictValue("jobs", attr_type=Job,
                                                         value=builds_out)
        get_deployment_output = AttributeDictValue("jobs", attr_type=Job,
                                                   value=deployment_out)
        jenkins_deployment.return_value = get_deployment_output
        with NamedTemporaryFile() as config_file:
            config_file.write(b"environments:\n")
            config_file.write(b"  env:\n")
            config_file.write(b"    system:\n")
            config_file.write(b"      system_type: jenkins\n")
            config_file.write(b"      sources:\n")
            config_file.write(b"        jenkins:\n")
            config_file.write(b"          driver: jenkins\n")
            config_file.write(b"          url: url\n")
            config_file.seek(0)
            sys.argv = ['cibyl', '-p', 'openstack', '-f', 'text', '--config',
                        config_file.name, 'query', '--last-build',
                        '--ip-version', '4']

            main()

        output = self.stdout
        self.assertIn("Job: job1", output)
        self.assertIn("Build: 1", output)
        self.assertIn("Openstack deployment:", output)
        self.assertIn("Network:", output)
        self.assertIn("IP version: 4", output)
        self.assertIn("Total jobs found in query: 1", output)

    @patch.object(Jenkins, 'setup', return_value="")
    @patch('cibyl.orchestrator.get_source_instance_from_method')
    @patch('cibyl.orchestrator.source_information_from_method',
           return_value="")
    @patch.object(Jenkins, 'get_tests', side_effect=JenkinsError)
    @patch.object(OSPJenkins, 'get_deployment', side_effect=JenkinsError)
    @patch('cibyl.plugins.get_classes_in', return_value=[OSPJenkins])
    def test_args_level_tests_and_deployment(self, _get_classes_mock,
                                             jenkins_deployment,
                                             jenkins_tests, _,
                                             source_instance_mock,
                                             jenkins_setup_mock):
        """Test that the args level is correctly considered and the correct
        number of source queries are done."""
        source_instance_mock.return_value = Jenkins(url="url")
        with NamedTemporaryFile() as config_file:
            config_file.write(b"environments:\n")
            config_file.write(b"  env:\n")
            config_file.write(b"    system:\n")
            config_file.write(b"      system_type: jenkins\n")
            config_file.write(b"      sources:\n")
            config_file.write(b"        jenkins:\n")
            config_file.write(b"          driver: jenkins\n")
            config_file.write(b"          url: url\n")
            config_file.seek(0)
            sys.argv = ['cibyl', '-p', 'openstack', '--config',
                        config_file.name, 'query', '--jobs', 'DFG-compute',
                        '--ip-version', '--tests']

            main()
        jenkins_deployment.assert_called_once()
        jenkins_tests.assert_called_once()
        jenkins_setup_mock.assert_called_once()

    @patch.object(Jenkins, 'setup', return_value="")
    @patch('cibyl.orchestrator.get_source_instance_from_method')
    @patch('cibyl.orchestrator.source_information_from_method',
           return_value="")
    @patch.object(Jenkins, 'get_builds', side_effect=JenkinsError)
    @patch.object(OSPJenkins, 'get_deployment', side_effect=JenkinsError)
    @patch('cibyl.plugins.get_classes_in', return_value=[OSPJenkins])
    def test_args_level_builds_and_deployment(self, _get_classes_mock,
                                              jenkins_deployment,
                                              jenkins_builds, _,
                                              source_instance_mock,
                                              jenkins_setup_mock):
        """Test that the args level is correctly considered and the correct
        number of source queries are done."""
        source_instance_mock.return_value = Jenkins(url="url")
        with NamedTemporaryFile() as config_file:
            config_file.write(b"environments:\n")
            config_file.write(b"  env:\n")
            config_file.write(b"    system:\n")
            config_file.write(b"      system_type: jenkins\n")
            config_file.write(b"      sources:\n")
            config_file.write(b"        jenkins:\n")
            config_file.write(b"          driver: jenkins\n")
            config_file.write(b"          url: url\n")
            config_file.seek(0)
            sys.argv = ['cibyl', '-p', 'openstack', '--config',
                        config_file.name, 'query', '--jobs', 'DFG-compute',
                        '--ip-version', '--builds']

            main()
        jenkins_deployment.assert_called_once()
        jenkins_builds.assert_called_once()
        jenkins_setup_mock.assert_called_once()

    @patch.object(Jenkins, 'setup', return_value="")
    @patch('cibyl.orchestrator.get_source_instance_from_method')
    @patch('cibyl.orchestrator.source_information_from_method',
           return_value="")
    @patch.object(Jenkins, 'get_tests', side_effect=JenkinsError)
    @patch.object(OSPJenkins, 'get_deployment', side_effect=JenkinsError)
    @patch('cibyl.plugins.get_classes_in', return_value=[OSPJenkins])
    def test_args_level_tests_and_packages(self, _get_classes_mock,
                                           jenkins_deployment,
                                           jenkins_tests, _,
                                           source_instance_mock,
                                           jenkins_setup_mock):
        """Test that the args level is correctly considered and the correct
        number of source queries are done."""
        source_instance_mock.return_value = Jenkins(url="url")
        with NamedTemporaryFile() as config_file:
            config_file.write(b"environments:\n")
            config_file.write(b"  env:\n")
            config_file.write(b"    system:\n")
            config_file.write(b"      system_type: jenkins\n")
            config_file.write(b"      sources:\n")
            config_file.write(b"        jenkins:\n")
            config_file.write(b"          driver: jenkins\n")
            config_file.write(b"          url: url\n")
            config_file.seek(0)
            sys.argv = ['cibyl', '-p', 'openstack', '--config',
                        config_file.name, 'query',
                        '--jobs', 'DFG-compute', '--ip-version', '--tests',
                        '--builds']

            main()
        jenkins_deployment.assert_called_once()
        jenkins_tests.assert_called_once()
        jenkins_setup_mock.assert_called_once()

    @skip("Should be skipped until get_tests is implemented in Zuul")
    @patch.object(Zuul, 'setup', return_value="")
    @patch('cibyl.orchestrator.get_source_instance_from_method')
    @patch('cibyl.orchestrator.source_information_from_method',
           return_value="")
    @patch.object(Zuul, 'get_tests', side_effect=JenkinsError)
    @patch.object(OSPZuul, 'get_deployment', side_effect=JenkinsError)
    @patch('cibyl.plugins.get_classes_in', return_value=[OSPZuul])
    def test_args_level_tests_and_deployment_zuul(self, _get_classes_mock,
                                                  zuul_deployment,
                                                  zuul_tests, _,
                                                  source_instance_mock,
                                                  zuul_setup_mock):
        """Test that the args level is correctly considered and the correct
        number of source queries are done."""
        source_instance_mock.return_value = Zuul(url="url", name="zuul",
                                                 driver="zuul")
        with NamedTemporaryFile() as config_file:
            config_file.write(b"environments:\n")
            config_file.write(b"  env:\n")
            config_file.write(b"    system:\n")
            config_file.write(b"      system_type: zuul\n")
            config_file.write(b"      sources:\n")
            config_file.write(b"        zuul:\n")
            config_file.write(b"          driver: zuul\n")
            config_file.write(b"          url: url\n")
            config_file.seek(0)
            sys.argv = ['cibyl', '-p', 'openstack', '--config',
                        config_file.name, 'query',
                        '--jobs', 'DFG-compute', '--ip-version', '--tests']

            main()
        zuul_deployment.assert_called_once()
        zuul_tests.assert_called_once()
        zuul_setup_mock.assert_called_once()

    @patch.object(Zuul, 'setup', return_value="")
    @patch('cibyl.orchestrator.get_source_instance_from_method')
    @patch('cibyl.orchestrator.source_information_from_method',
           return_value="")
    @patch.object(Zuul, 'get_builds', side_effect=JenkinsError)
    @patch.object(OSPZuul, 'get_deployment', side_effect=JenkinsError)
    @patch('cibyl.plugins.get_classes_in', return_value=[OSPZuul])
    def test_args_level_builds_and_deployment_zuul(self, _get_classes_mock,
                                                   zuul_deployment,
                                                   zuul_builds, _,
                                                   source_instance_mock,
                                                   zuul_setup_mock):
        """Test that the args level is correctly considered and the correct
        number of source queries are done."""
        source_instance_mock.return_value = Zuul(name="zuul", driver="zuul",
                                                 url="url")
        with NamedTemporaryFile() as config_file:
            config_file.write(b"environments:\n")
            config_file.write(b"  env:\n")
            config_file.write(b"    system:\n")
            config_file.write(b"      system_type: zuul\n")
            config_file.write(b"      sources:\n")
            config_file.write(b"        zuul:\n")
            config_file.write(b"          driver: zuul\n")
            config_file.write(b"          url: url\n")
            config_file.seek(0)
            sys.argv = ['cibyl', '-p', 'openstack', '--config',
                        config_file.name, 'query',
                        '--jobs', 'DFG-compute', '--ip-version', '--builds']

            main()
        zuul_deployment.assert_called_once()
        zuul_builds.assert_called_once()
        zuul_setup_mock.assert_called_once()

    @patch('cibyl.sources.source.get_source_method')
    @patch.object(ElasticSearch, 'setup', side_effect=JenkinsError)
    @patch('cibyl.orchestrator.get_source_instance_from_method')
    @patch('cibyl.orchestrator.source_information_from_method',
           return_value="")
    @patch.object(Jenkins, 'get_builds', side_effect=JenkinsError)
    def test_error_setup_caught(self, jenkins_builds, _, source_instance_mock,
                                elasticsearch_setup, get_source_mock):
        """Test that an error in the source setup is caught and the next
        source is called."""
        elk_source = ElasticSearch(name="elk", driver="elasticsearch",
                                   url="url")
        source_instance_mock.side_effect = [elk_source,
                                            Jenkins(url="url")]
        get_source_mock.return_value = [(elk_source.get_builds, 2),
                                        (jenkins_builds, 1)]
        with NamedTemporaryFile() as config_file:
            config_file.write(b"environments:\n")
            config_file.write(b"  env:\n")
            config_file.write(b"    system:\n")
            config_file.write(b"      system_type: jenkins\n")
            config_file.write(b"      sources:\n")
            config_file.write(b"        jenkins:\n")
            config_file.write(b"          driver: jenkins\n")
            config_file.write(b"          url: url\n")
            config_file.write(b"        elk:\n")
            config_file.write(b"          driver: elasticsearch\n")
            config_file.write(b"          url: url\n")
            config_file.seek(0)
            sys.argv = ['cibyl', '--config', config_file.name,
                        'query', '--builds', 'DFG-compute']

            main()
        elasticsearch_setup.assert_called_once()
        jenkins_builds.assert_called_once()

    @patch('cibyl.orchestrator.get_source_instance_from_method')
    @patch('cibyl.orchestrator.source_information_from_method',
           return_value="")
    @patch.object(OSPJenkins, 'get_deployment', side_effect=JenkinsError)
    @patch('cibyl.plugins.get_classes_in', return_value=[OSPJenkins])
    def test_spec_subcommand(self, _get_classes_mock, jenkins_deployment, _,
                             source_instance_mock):
        """Test that calling the spec subcommand passed the argument to the
        source."""
        source_instance_mock.return_value = Jenkins(url="url")
        with NamedTemporaryFile() as config_file:
            config_file.write(b"environments:\n")
            config_file.write(b"  env:\n")
            config_file.write(b"    system:\n")
            config_file.write(b"      system_type: jenkins\n")
            config_file.write(b"      sources:\n")
            config_file.write(b"        jenkins:\n")
            config_file.write(b"          driver: jenkins\n")
            config_file.write(b"          url: url\n")
            config_file.seek(0)
            sys.argv = ['cibyl', '-p', 'openstack', '--config',
                        config_file.name, 'spec', 'DFG-compute']
            main()
        jenkins_deployment.assert_called_once()
        _, arguments = jenkins_deployment.call_args
        self.assertIn("spec", arguments)
        self.assertEqual(["DFG-compute"], arguments["spec"].value)

    def test_spec_subcommand_no_args(self):
        """Test that calling the spec subcommand without any argument fails."""
        with NamedTemporaryFile() as config_file:
            config_file.write(b"environments:\n")
            config_file.write(b"  env:\n")
            config_file.write(b"    system:\n")
            config_file.write(b"      system_type: jenkins\n")
            config_file.write(b"      sources:\n")
            config_file.write(b"        jenkins:\n")
            config_file.write(b"          driver: jenkins\n")
            config_file.write(b"          url: url\n")
            config_file.seek(0)
            sys.argv = ['cibyl', '-p', 'openstack', '--config',
                        config_file.name, 'spec']
            with self.assertRaises(SystemExit):
                main()

    def test_spec_subcommand_many_args(self):
        """Test that calling the spec subcommand with more than
        one argument fails."""
        with NamedTemporaryFile() as config_file:
            config_file.write(b"environments:\n")
            config_file.write(b"  env:\n")
            config_file.write(b"    system:\n")
            config_file.write(b"      system_type: jenkins\n")
            config_file.write(b"      sources:\n")
            config_file.write(b"        jenkins:\n")
            config_file.write(b"          driver: jenkins\n")
            config_file.write(b"          url: url\n")
            config_file.seek(0)
            sys.argv = ['cibyl', '-p', 'openstack', '--config',
                        config_file.name, 'spec', 'job1', 'job2']
            with self.assertRaises(SystemExit):
                main()
