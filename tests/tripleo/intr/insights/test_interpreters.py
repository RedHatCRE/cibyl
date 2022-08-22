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
from tempfile import TemporaryDirectory
from unittest import TestCase

from tripleo.insights.exceptions import IllegibleData
from tripleo.insights.interpreters import (EnvironmentInterpreter,
                                           FeatureSetInterpreter,
                                           NodesInterpreter,
                                           ReleaseInterpreter)
from tripleo.utils.fs import cd_context_manager


class TestEnvironmentInterpreter(TestCase):
    """Tests for :class:`EnvironmentInterpreter`.
    """

    def test_error_on_invalid_infra_type(self):
        """Tests that an error is thrown if the infra_type field does not
        follow the schema.
        """
        data = {
            EnvironmentInterpreter.Keys().infra_type: False
        }

        with self.assertRaises(IllegibleData):
            EnvironmentInterpreter(data)

    def test_default_schema_path_outside_repo(self):
        """Test that the default path for the schema file can be read properly
        from a random directory, different from the cibyl source directory."""

        data = {}

        with TemporaryDirectory() as tempdir:
            with cd_context_manager(tempdir):
                EnvironmentInterpreter(data)


class TestFeatureSetInterpreter(TestCase):
    """Tests for :class:`FeatureSetInterpreter`.
    """

    def test_error_on_invalid_ipv6(self):
        """Tests that an error is thrown if the ipv6 field does not follow the
        schema.
        """
        data = {
            FeatureSetInterpreter.Keys().ipv6: 'hello_world'  # Must be bool
        }

        with self.assertRaises(IllegibleData):
            FeatureSetInterpreter(data)

    def test_default_schema_path_outside_repo(self):
        """Test that the default path for the schema file can be read properly
        from a random directory, different from the cibyl source directory."""

        data = {}

        with TemporaryDirectory() as tempdir:
            with cd_context_manager(tempdir):
                FeatureSetInterpreter(data)


class TestNodesInterpreter(TestCase):
    """Tests for :class:`NodesInterpreter`.
    """

    def test_error_on_invalid_topology(self):
        """Tests that an error is thrown if the 'topology_map' field does
        not follow the schema.
        """
        data = {
            NodesInterpreter.Keys().root.topology: False  # Must be an object
        }

        with self.assertRaises(IllegibleData):
            NodesInterpreter(data)

    def test_default_schema_path_outside_repo(self):
        """Test that the default path for the schema file can be read properly
        from a random directory, different from the cibyl source directory."""

        data = {}

        with TemporaryDirectory() as tempdir:
            with cd_context_manager(tempdir):
                NodesInterpreter(data)


class TestReleaseInterpreter(TestCase):
    """Tests for :class:`TestReleaseInterpreter`.
    """

    def test_error_on_invalid_release(self):
        """Tests that an error if the release field is not present.
        """
        data = {
            ReleaseInterpreter.Keys().release: False  # Must be string
        }

        with self.assertRaises(IllegibleData):
            ReleaseInterpreter(data)

    def test_default_schema_path_outside_repo(self):
        """Test that the default path for the schema file can be read properly
        from a random directory, different from the cibyl source directory."""

        data = {}

        with TemporaryDirectory() as tempdir:
            with cd_context_manager(tempdir):
                ReleaseInterpreter(data)
