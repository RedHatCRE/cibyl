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
from copy import deepcopy
from tempfile import NamedTemporaryFile

from cibyl.cli.main import main
from cibyl.models.ci.base.job import Job as BaseJob
from cibyl.models.ci.base.system import System
from cibyl.models.ci.zuul.job import Job as ZuulJob
from tests.cibyl.utils import RestoreAPIs


class TestOpenstackCLI(RestoreAPIs):
    """Tests that openstack arguments are added to cli."""

    @classmethod
    def setUpClass(cls):
        cls.original_job_api = deepcopy(BaseJob.API)
        cls.original_system_api = deepcopy(System.API)
        cls._null_stdout = open(os.devnull, 'w', encoding='utf-8')
        super().setUpClass()
        cls._original_stdout = sys.stdout
        # silence stdout and logging to avoid cluttering
        logging.disable(logging.CRITICAL)
        sys.stdout = cls._null_stdout

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        sys.stdout = cls._original_stdout
        cls._null_stdout.close()

    def setUp(self):
        # restore Job API before each test
        BaseJob.API = deepcopy(self.original_job_api)
        System.API = deepcopy(self.original_system_api)

    def test_openstack_cli_zuul_system(self):
        """Test that the Deployment model is added to the Variant when a Zuul
        system is present in the configuration.
        """
        with NamedTemporaryFile() as config_file:
            config_file.write(b"environments:\n")
            config_file.write(b"  env:\n")
            config_file.write(b"    system:\n")
            config_file.write(b"      system_type: zuul\n")
            config_file.write(b"      sources: {}\n")
            config_file.seek(0)
            sys.argv = ['query', '-h', '-p', 'openstack', '--config',
                        config_file.name]

            with self.assertRaises(SystemExit):
                main()
        self.assertIn('deployment', ZuulJob.Variant.API)

    def test_openstack_cli_jenkins_system(self):
        """Test that the Deployment model is added to the Job when a Jenkins
        system is present in the configuration.
        """
        with NamedTemporaryFile() as config_file:
            config_file.write(b"environments:\n")
            config_file.write(b"  env:\n")
            config_file.write(b"    system:\n")
            config_file.write(b"      system_type: jenkins\n")
            config_file.write(b"      sources: {}\n")
            config_file.seek(0)
            sys.argv = ['query', '-h', '-p', 'openstack', '--config',
                        config_file.name]

            with self.assertRaises(SystemExit):
                main()
        self.assertIn('deployment', BaseJob.API)

    def test_openstack_cli_zuul_jenkins_system(self):
        """Test that the Deployment model is added to the Variant when a
        Zuul system is present in the configuration.
        """
        with NamedTemporaryFile() as config_file:
            config_file.write(b"environments:\n")
            config_file.write(b"  env:\n")
            config_file.write(b"    system:\n")
            config_file.write(b"      system_type: zuul\n")
            config_file.write(b"      sources: {}\n")
            config_file.write(b"    system2:\n")
            config_file.write(b"      system_type: jenkins\n")
            config_file.write(b"      sources: {}\n")
            config_file.seek(0)
            sys.argv = ['query', '-h', '-p', 'openstack', '--config',
                        config_file.name]

            with self.assertRaises(SystemExit):
                main()
        self.assertIn('deployment', ZuulJob.Variant.API)

    def test_openstack_cli_jenkins_zuul_system(self):
        """Test that the Deployment model is added to the Job when a Jenkins
        system is present in the configuration.
        """
        with NamedTemporaryFile() as config_file:
            config_file.write(b"environments:\n")
            config_file.write(b"  env:\n")
            config_file.write(b"    system:\n")
            config_file.write(b"      system_type: jenkins\n")
            config_file.write(b"      sources: {}\n")
            config_file.write(b"    system2:\n")
            config_file.write(b"      system_type: zuul\n")
            config_file.write(b"      sources: {}\n")
            config_file.seek(0)
            sys.argv = ['query', '-h', '-p', 'openstack', '--config',
                        config_file.name]

            with self.assertRaises(SystemExit):
                main()
        self.assertIn('deployment', BaseJob.API)

    def test_openstack_cli_zuul_system_plugin_configuration(self):
        """Test that the Deployment model is added to the Variant when a Zuul
        system is present in the configuration and openstack plugin is added
        through the configuration.
        """
        with NamedTemporaryFile() as config_file:
            config_file.write(b"environments:\n")
            config_file.write(b"  env:\n")
            config_file.write(b"    system:\n")
            config_file.write(b"      system_type: zuul\n")
            config_file.write(b"      sources: {}\n")
            config_file.write(b"plugins:\n")
            config_file.write(b"  - openstack\n")
            config_file.seek(0)
            sys.argv = ['cibyl', 'query', '-h', '--config', config_file.name]

            with self.assertRaises(SystemExit):
                main()
        self.assertIn('deployment', ZuulJob.Variant.API)
