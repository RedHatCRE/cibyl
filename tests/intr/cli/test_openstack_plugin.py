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
from copy import deepcopy
from tempfile import NamedTemporaryFile
from unittest import TestCase

from cibyl.cli.main import main
from cibyl.models.ci.job import Job
from cibyl.models.ci.system import System


class TestOpenstackCLI(TestCase):
    """Tests that openstack arguments are added to cli."""

    @classmethod
    def setUpClass(cls):
        cls.original_job_api = deepcopy(Job.API)
        cls.original_system_api = deepcopy(System.API)

    def setUp(self):
        # restore Job API before each test
        Job.API = deepcopy(self.original_job_api)
        System.API = deepcopy(self.original_system_api)
        # silence stdout and logging to avoid cluttering
        sys.stdout = None
        logging.disable(logging.CRITICAL)

    def test_openstack_cli_zuul_system(self):
        """Test that the Deployment model is added to the Job when a Zuul
        system is present in the configuration.
        """
        with NamedTemporaryFile() as config_file:
            config_file.write(b"environments:\n")
            config_file.write(b"  env:\n")
            config_file.write(b"    system:\n")
            config_file.write(b"      system_type: zuul\n")
            config_file.seek(0)
            sys.argv = ['-h', '-p', 'openstack', '--config', config_file.name]

            main()
        self.assertIn('deployment', Job.API)

    def test_openstack_cli_jenkins_system(self):
        """Test that the Deployment model is added to the Job when a Jenkins
        system is present in the configuration.
        """
        with NamedTemporaryFile() as config_file:
            config_file.write(b"environments:\n")
            config_file.write(b"  env:\n")
            config_file.write(b"    system:\n")
            config_file.write(b"      system_type: jenkins\n")
            config_file.seek(0)
            sys.argv = ['-h', '-p', 'openstack', '--config', config_file.name]

            main()
        self.assertIn('deployment', Job.API)

    def test_openstack_cli_zuul_jenkins_system(self):
        """Test that the Deployment model is added to the Job when a Jenkins
        system is present in the configuration.
        """
        with NamedTemporaryFile() as config_file:
            config_file.write(b"environments:\n")
            config_file.write(b"  env:\n")
            config_file.write(b"    system:\n")
            config_file.write(b"      system_type: zuul\n")
            config_file.write(b"    system2:\n")
            config_file.write(b"      system_type: jenkins\n")
            config_file.seek(0)
            sys.argv = ['-h', '-p', 'openstack', '--config', config_file.name]

            main()
        self.assertIn('deployment', Job.API)

    def test_openstack_cli_jenkins_zuul_system(self):
        """Test that the Deployment model is added to the Job when a Jenkins
        system is present in the configuration.
        """
        with NamedTemporaryFile() as config_file:
            config_file.write(b"environments:\n")
            config_file.write(b"  env:\n")
            config_file.write(b"    system:\n")
            config_file.write(b"      system_type: jenkins\n")
            config_file.write(b"    system2:\n")
            config_file.write(b"      system_type: zuul\n")
            config_file.seek(0)
            sys.argv = ['-h', '-p', 'openstack', '--config', config_file.name]

            main()
        self.assertIn('deployment', Job.API)
