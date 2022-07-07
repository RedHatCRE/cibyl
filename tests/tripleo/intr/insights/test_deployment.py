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

from tripleo.insights.deployment import (EnvironmentInterpreter,
                                         FeatureSetInterpreter)
from tripleo.insights.exceptions import IllegibleData


class TestEnvironmentInterpreter(TestCase):
    """Tests for :class:`EnvironmentInterpreter`.
    """

    def test_error_on_invalid_infra_type(self):
        """Tests that an error is thrown if the infra_type field does not
        follow the schema.
        """
        data = {
            EnvironmentInterpreter.KEYS.infra_type: False
        }

        with self.assertRaises(IllegibleData):
            EnvironmentInterpreter(data)


class TestFeatureSetInterpreter(TestCase):
    """Tests for :class:`FeatureSetInterpreter`.
    """

    def tests_error_on_invalid_ipv6(self):
        """Tests that an error is thrown if the ipv6 field does not follow the
        schema.
        """
        data = {
            FeatureSetInterpreter.KEYS.ipv6: 'hello_world'  # Must be bool
        }

        with self.assertRaises(IllegibleData):
            FeatureSetInterpreter(data)