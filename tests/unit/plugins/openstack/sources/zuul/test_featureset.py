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

from cibyl.plugins.openstack.sources.zuul.featureset import FeatureSetFinder


class TestFeatureSet(TestCase):
    """Tests for :class:`FeatureSet`.
    """

    def test_finds_featureset_in_variant(self):
        """Checks that the featureset is found if one of the search terms
        appear on the variant's variables.
        """
        featureset = '052'

        variant = Mock()
        variant.variables = Mock()
        variant.variables.return_value = {
            'featureset': featureset
        }

        finder = FeatureSetFinder()

        self.assertEqual(
            featureset,
            finder.find_featureset_in(variant)
        )

        variant.variables.assert_called_once_with(recursive=True)

    def test_finds_overrides_in_variant(self):
        """Checks that the featureset overrides are found if one of the search
        terms appear on the variant's variables.
        """
        overrides = {
            'val1': 'var1'
        }

        variant = Mock()
        variant.variables = Mock()
        variant.variables.return_value = {
            'featureset_override': overrides
        }

        finder = FeatureSetFinder()

        self.assertEqual(
            overrides,
            finder.find_overrides_in(variant)
        )

        variant.variables.assert_called_once_with(recursive=True)

    def test_result_not_found(self):
        """Checks the returned value if the search terms were not found.
        """
        variant = Mock()
        variant.variables = Mock()
        variant.variables.return_value = {
        }

        finder = FeatureSetFinder()

        self.assertEqual(
            None,
            finder.find_featureset_in(variant)
        )

        self.assertEqual(
            None,
            finder.find_overrides_in(variant)
        )
