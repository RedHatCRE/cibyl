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
from unittest.mock import Mock

from tripleo.insights.deployment import FeatureSetInterpreter


class TestFeatureSetInterpreter(TestCase):
    """Tests for :class:`FeatureSetInterpreter`.
    """

    def test_checks_data_validity(self):
        """Verifies that the class checks that the data follows the schema.
        """
        data = {}
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
            validator_factory=factory
        )

        factory.from_file.assert_called_once_with(schema)

        validator.is_valid.assert_called_once_with(data)

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

        with self.assertRaises(ValueError):
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
