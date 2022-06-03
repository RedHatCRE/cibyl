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
import os
import sys
from tempfile import NamedTemporaryFile
from unittest import TestCase
from unittest.mock import patch

from cibyl.cli.main import main
from cibyl.exceptions.jenkins import JenkinsError
from cibyl.plugins.openstack.sources.jenkins import Jenkins as OSPJenkins
from cibyl.sources.jenkins import Jenkins
from cibyl.utils.source_methods_store import SourceMethodsStore


class TestOrchestrator(TestCase):
    """Test the Orchestrator class."""

    @classmethod
    def setUpClass(cls):
        cls._null_stdout = open(os.devnull, 'w', encoding='utf-8')
        cls._original_stdout = sys.stdout
        # silence stdout and logging to avoid cluttering
        logging.disable(logging.CRITICAL)
        sys.stdout = cls._null_stdout

    @classmethod
    def tearDownClass(cls):
        sys.stdout = cls._original_stdout
        cls._null_stdout.close()

    @patch('cibyl.orchestrator.source_information_from_method',
           return_value="")
    @patch.object(SourceMethodsStore, '_method_information_tuple')
    @patch.object(Jenkins, 'get_jobs', side_effect=JenkinsError)
    @patch.object(OSPJenkins, 'get_deployment', side_effect=JenkinsError)
    @patch('cibyl.plugins.get_classes_in', return_value=[OSPJenkins])
    def test_args_level(self, _get_classes_mock, jenkins_deployment,
                        jenkins_jobs, store_mock, _):
        """Test that the args level is updated properly in run_query."""
        store_mock.side_effect = [("jenkins", "get_deployment"),
                                  ("jenkins", "get_deployment"),
                                  ("jenkins", "get_jobs"),
                                  ("jenkins", "get_jobs"),
                                  ("jenkins", "get_jobs")]
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
            sys.argv = ['', '-p', 'openstack', '--config', config_file.name,
                        '--jobs', 'DFG-compute', '--spec']

            main()
        jenkins_deployment.assert_called_once()
        jenkins_jobs.assert_not_called()
