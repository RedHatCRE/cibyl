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
from io import StringIO
from tempfile import NamedTemporaryFile
from unittest import TestCase

from cibyl.cli.main import main
from cibyl.exceptions.config import EmptyConfiguration


class TestConfig(TestCase):
    """Test that configuration is read properly when calling cibyl."""

    def test_empty_config(self):
        """Test that an exception is raised when calling cibyl with an empty
        configuration.
        """
        with NamedTemporaryFile() as config_file:
            sys.argv = [
                '',
                '--config', config_file.name,
                '--debug'
            ]

            self.assertRaises(EmptyConfiguration, main)


class TestConfigHelp(TestCase):
    """Test that configuration is read and the help message is displayed when
    calling cibyl with the help option."""

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

    def test_empty_config_help(self):
        """Test that the help message is printed when calling cibyl with an
        empty configuration and the --help flag.
        """
        with NamedTemporaryFile() as config_file:
            sys.argv = [
                'cibyl', 'query',
                '--config', config_file.name,
                '--help'
            ]
            self.assertRaises(SystemExit, main)
        self.assertIn("usage: cibyl query [-h]", self.stdout)

    def test_valid_config_help(self):
        """Test that the help message is printed when calling cibyl with an
        empty configuration and the --help flag.
        """
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
            sys.argv = [
                'cibyl',
                'query',
                '--config', config_file.name,
                '--jobs',
                '--help'
            ]
            self.assertRaises(SystemExit, main)
        self.assertIn("usage: cibyl query [-h]", self.stdout)
