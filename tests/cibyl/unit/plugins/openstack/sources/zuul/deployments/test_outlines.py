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

from cibyl.plugins.openstack.sources.zuul.deployments.outlines import (
    FeatureSetFetcher, OutlineCreator, OverridesCollector)
from tripleo.insights.defaults import DEFAULT_FEATURESET_FILE


class TestOverridesCollector(TestCase):
    """Tests for :class:`OverridesCollector`.
    """

    def test_no_infra_type(self):
        """Tests that the result is not modified if there is not
        'infra_type' override.
        """
        overrides = {}

        variant = Mock()

        search = Mock()
        search.search = Mock()
        search.search.return_value = None

        tools = Mock()
        tools.infra_type_search = search

        collector = OverridesCollector(tools)

        result = collector.collect_overrides_for(variant)

        self.assertEqual(overrides, result)

        search.search.assert_called_once_with(variant)

    def test_infra_type(self):
        """Checks that an override for 'infra_type' is found.
        """
        infra_type_var = 'infra_type'
        infra_type_val = 'ovb'

        overrides = {
            infra_type_var: infra_type_val
        }

        variant = Mock()

        search = Mock()
        search.search = Mock()
        search.search.return_value = (infra_type_var, infra_type_val)

        tools = Mock()
        tools.infra_type_search = search

        collector = OverridesCollector(tools)

        result = collector.collect_overrides_for(variant)

        self.assertEqual(overrides, result)

        search.search.assert_called_once_with(variant)


class TestFeatureSetFetcher(TestCase):
    """Tests for :class:`FeatureSetFetcher`.
    """

    def test_no_custom_featureset(self):
        """Checks that the default value is returned if the variant has no
        custom featureset.
        """
        default = 'path'

        variant = Mock()

        search = Mock()
        search.search = Mock()
        search.search.return_value = None

        tools = Mock()
        tools.featureset_search = search

        fetcher = FeatureSetFetcher(tools)

        result = fetcher.fetch_featureset(variant, default)

        self.assertEqual(default, result)

    def test_custom_featureset(self):
        """Checks that this generates the featureset path from the
        variant's variables.
        """
        fs = '001'
        file = 'some_file.yml'
        path = 'path/to/some_file.yml'

        variant = Mock()

        files = Mock()
        files.create_featureset = Mock()
        files.create_featureset.return_value = file

        paths = Mock()
        paths.create_featureset_path = Mock()
        paths.create_featureset_path.return_value = path

        search = Mock()
        search.search = Mock()
        search.search.return_value = ('var', fs)

        tools = Mock()
        tools.quickstart_files = files
        tools.quickstart_paths = paths
        tools.featureset_search = search

        fetcher = FeatureSetFetcher(tools)

        result = fetcher.fetch_featureset(variant, 'unused')

        self.assertEqual(path, result)

        search.search.assert_called_once_with(variant)
        files.create_featureset.assert_called_once_with(fs)
        paths.create_featureset_path.assert_called_once_with(file)


class TestOutlineCreator(TestCase):
    """Tests for :class:`OutlineCreator`.
    """

    def test_fetches_featureset(self):
        """Checks that this will read the featureset from the variant. Also
        checks the default value it will use if there is no custom
        featureset on the variant.
        """
        featureset = 'some_value'

        variant = Mock()

        fetcher = Mock()
        fetcher.fetch_featureset = Mock()
        fetcher.fetch_featureset.return_value = featureset

        tools = Mock()
        tools.featureset_fetcher = fetcher

        creator = OutlineCreator(tools)

        result = creator.new_outline_for(variant)

        self.assertEqual(featureset, result.featureset)

        fetcher.fetch_featureset.assert_called_once_with(
            variant,
            DEFAULT_FEATURESET_FILE
        )

    def test_fetches_overrides(self):
        """Checks that this will read all possible overrides from the variant.
        """
        overrides = {
            'var1': 'val1'
        }

        variant = Mock()

        collector = Mock()
        collector.collect_overrides_for = Mock()
        collector.collect_overrides_for.return_value = overrides

        tools = Mock()
        tools.overrides_collector = collector

        creator = OutlineCreator(tools)

        result = creator.new_outline_for(variant)

        self.assertEqual(overrides, result.overrides)

        collector.collect_overrides_for.assert_called_once_with(variant)
