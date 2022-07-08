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
from unittest.mock import Mock, call

from tripleo.insights.deployment import (EnvironmentInterpreter,
                                         FeatureSetInterpreter,
                                         NodesInterpreter)
from tripleo.insights.exceptions import IllegibleData
from tripleo.insights.io import Topology


class TestEnvironmentInterpreter(TestCase):
    """Tests for :class:`EnvironmentInterpreter`.
    """

    def test_checks_data_validity(self):
        """Verifies that the class checks that the data follows the schema.
        """
        data = {}
        overrides = {}

        schema = Mock()

        validator = Mock()
        validator.is_valid = Mock()
        validator.is_valid.return_value = True

        factory = Mock()
        factory.from_file = Mock()
        factory.from_file.return_value = validator

        EnvironmentInterpreter(
            data,
            schema=schema,
            overrides=overrides,
            validator_factory=factory
        )

        factory.from_file.assert_called_once_with(schema)

        validator.is_valid.assert_has_calls(
            [
                call(data),
                call(overrides)
            ]
        )

    def test_error_if_invalid_data(self):
        """Checks that an error is thrown if the data is not valid.
        """
        data = {}

        schema = Mock()

        validator = Mock()
        validator.is_valid = Mock()
        validator.is_valid.return_value = False

        factory = Mock()
        factory.from_file = Mock()
        factory.from_file.return_value = validator

        with self.assertRaises(IllegibleData):
            EnvironmentInterpreter(
                data,
                schema=schema,
                validator_factory=factory
            )

    def test_get_infra_type(self):
        """Checks that it is able to extract the infrastructure type.
        """
        keys = EnvironmentInterpreter.KEYS

        infra_type = 'libvirt'

        data = {}

        schema = Mock()

        validator = Mock()
        validator.is_valid = Mock()
        validator.is_valid.return_value = True

        factory = Mock()
        factory.from_file = Mock()
        factory.from_file.return_value = validator

        environment = EnvironmentInterpreter(
            data,
            schema=schema,
            validator_factory=factory
        )

        self.assertEqual(None, environment.get_intra_type())

        data[keys.infra_type] = infra_type

        self.assertEqual(infra_type, environment.get_intra_type())

    def test_override_infra_type(self):
        """Checks that the value of the 'overrides' dictionary is chosen
        before the one from the file.
        """
        keys = EnvironmentInterpreter.KEYS

        infra_type = 'libvirt'
        override = 'ovb'

        data = {keys.infra_type: infra_type}
        overrides = {keys.infra_type: override}

        schema = Mock()

        validator = Mock()
        validator.is_valid = Mock()
        validator.is_valid.return_value = True

        factory = Mock()
        factory.from_file = Mock()
        factory.from_file.return_value = validator

        environment = EnvironmentInterpreter(
            data,
            schema=schema,
            overrides=overrides,
            validator_factory=factory
        )

        self.assertEqual(override, environment.get_intra_type())


class TestFeatureSetInterpreter(TestCase):
    """Tests for :class:`FeatureSetInterpreter`.
    """

    def test_checks_data_validity(self):
        """Verifies that the class checks that the data follows the schema.
        """
        data = {}
        overrides = {}

        schema = Mock()

        validator = Mock()
        validator.is_valid = Mock()
        validator.is_valid.return_value = True

        factory = Mock()
        factory.from_file = Mock()
        factory.from_file.return_value = validator

        FeatureSetInterpreter(
            data,
            schema=schema,
            overrides=overrides,
            validator_factory=factory
        )

        factory.from_file.assert_called_once_with(schema)

        validator.is_valid.assert_has_calls(
            [
                call(data),
                call(overrides)
            ]
        )

    def test_error_if_invalid_data(self):
        """Checks that an error is thrown if the data is not valid.
        """
        data = {}

        schema = Mock()

        validator = Mock()
        validator.is_valid = Mock()
        validator.is_valid.return_value = False

        factory = Mock()
        factory.from_file = Mock()
        factory.from_file.return_value = validator

        with self.assertRaises(IllegibleData):
            FeatureSetInterpreter(
                data,
                schema=schema,
                validator_factory=factory
            )

    def test_is_ipv6(self):
        """Checks that it is able to tell if the deployment is IPv4 or IPv6.
        """
        keys = FeatureSetInterpreter.KEYS

        data = {}

        schema = Mock()

        validator = Mock()
        validator.is_valid = Mock()
        validator.is_valid.return_value = True

        factory = Mock()
        factory.from_file = Mock()
        factory.from_file.return_value = validator

        featureset = FeatureSetInterpreter(
            data,
            schema=schema,
            validator_factory=factory
        )

        self.assertFalse(featureset.is_ipv6())

        data[keys.ipv6] = False

        self.assertFalse(featureset.is_ipv6())

        data[keys.ipv6] = True

        self.assertTrue(featureset.is_ipv6())

    def test_override_is_ipv6(self):
        """Checks that the value of the 'overrides' dictionary is chosen
        before the one from the file.
        """
        keys = FeatureSetInterpreter.KEYS

        ip_version = True
        override = False

        data = {keys.ipv6: ip_version}
        overrides = {keys.ipv6: override}

        schema = Mock()

        validator = Mock()
        validator.is_valid = Mock()
        validator.is_valid.return_value = True

        factory = Mock()
        factory.from_file = Mock()
        factory.from_file.return_value = validator

        featureset = FeatureSetInterpreter(
            data,
            schema=schema,
            overrides=overrides,
            validator_factory=factory
        )

        self.assertEqual(False, featureset.is_ipv6())


class TestNodesInterpreter(TestCase):
    """Tests for :class:`NodesInterpreter`.
    """

    def test_checks_data_validity(self):
        """Verifies that the class checks that the data follows the schema.
        """
        data = {}
        overrides = {}

        schema = Mock()

        validator = Mock()
        validator.is_valid = Mock()
        validator.is_valid.return_value = True

        factory = Mock()
        factory.from_file = Mock()
        factory.from_file.return_value = validator

        NodesInterpreter(
            data,
            schema=schema,
            overrides=overrides,
            validator_factory=factory
        )

        factory.from_file.assert_called_once_with(schema)

        validator.is_valid.assert_has_calls(
            [
                call(data),
                call(overrides)
            ]
        )

    def test_error_if_invalid_data(self):
        """Checks that an error is thrown if the data is not valid.
        """
        data = {}

        schema = Mock()

        validator = Mock()
        validator.is_valid = Mock()
        validator.is_valid.return_value = False

        factory = Mock()
        factory.from_file = Mock()
        factory.from_file.return_value = validator

        with self.assertRaises(IllegibleData):
            NodesInterpreter(
                data,
                schema=schema,
                validator_factory=factory
            )

    def test_get_topology(self):
        """Checks that the topology map is built from the data on the file.
        """
        keys = NodesInterpreter.KEYS

        data = {
            keys.topology: {
                'Controller': {
                    'scale': 1
                },
                'Compute': {
                    'scale': 3
                },
                'CephStorage': {
                    'scale': 2
                },
                'CellController': {
                    'scale': 1
                }
            }
        }

        schema = Mock()

        validator = Mock()
        validator.is_valid = Mock()
        validator.is_valid.return_value = True

        factory = Mock()
        factory.from_file = Mock()
        factory.from_file.return_value = validator

        nodes = NodesInterpreter(
            data,
            schema=schema,
            validator_factory=factory
        )

        result = nodes.get_topology()

        self.assertEqual(
            Topology(3, 1, 2, 1),
            result
        )

    def test_overrides_get_topology(self):
        """Checks that the topology map can be overridden.
        """
        keys = NodesInterpreter.KEYS

        data = {}
        overrides = {
            keys.topology: {
                'Controller': {
                    'scale': 1
                },
                'Compute': {
                    'scale': 3
                },
                'CephStorage': {
                    'scale': 2
                },
                'CellController': {
                    'scale': 1
                }
            }
        }

        schema = Mock()

        validator = Mock()
        validator.is_valid = Mock()
        validator.is_valid.return_value = True

        factory = Mock()
        factory.from_file = Mock()
        factory.from_file.return_value = validator

        nodes = NodesInterpreter(
            data,
            schema=schema,
            overrides=overrides,
            validator_factory=factory
        )

        result = nodes.get_topology()

        self.assertEqual(
            Topology(3, 1, 2, 1),
            result
        )
