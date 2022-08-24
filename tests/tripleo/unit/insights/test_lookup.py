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

from tripleo.insights.lookup import ScenarioFactory


class TestScenarioFactory(TestCase):
    """Tests for :class:`ScenarioFactory`.
    """

    def test_error_if_no_scenario(self):
        """Checks that an error is thrown if the featureset has no scenario.
        """
        cache = Mock()

        featureset = Mock()
        featureset.get_scenario = Mock()
        featureset.get_scenario.return_value = None

        factory = ScenarioFactory(cache=cache)

        with self.assertRaises(ValueError):
            factory.from_interpreters(
                outline=Mock(),
                featureset=featureset,
                release=Mock()
            )
