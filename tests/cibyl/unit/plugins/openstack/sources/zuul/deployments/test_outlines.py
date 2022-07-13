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
    FilesFetcher, OutlineCreator, OverridesCollector)
from tripleo.insights.defaults import (DEFAULT_FEATURESET_FILE,
                                       DEFAULT_NODES_FILE,
                                       DEFAULT_RELEASE_FILE)


class TestOverridesCollector(TestCase):
    """Tests for :class:`OverridesCollector`.
    """

    def test_no_infra_type(self):
        """Checks that the default override for 'infra_type' is returned in
        case the variant does not have a custom one for it.
        """
        default_key = 'key'
        default_val = 'val'

        defaults = Mock()
        defaults.infra_type = (default_key, default_val)

        variant = Mock()

        search = Mock()
        search.search = Mock()
        search.search.return_value = None

        tools = Mock()
        tools.infra_type_search = search

        collector = OverridesCollector(
            defaults=defaults,
            tools=tools
        )

        result = collector.collect_overrides_for(variant)

        self.assertEqual({default_key: default_val}, result)

        search.search.assert_called_once_with(variant)

    def test_infra_type(self):
        """Checks that an override for 'infra_type' is found.
        """
        infra_type_var = 'infra_type'
        infra_type_val = 'ovb'

        defaults = Mock()
        defaults.infra_type = (infra_type_var, 'libvirt')

        variant = Mock()

        search = Mock()
        search.search = Mock()
        search.search.return_value = (infra_type_var, infra_type_val)

        tools = Mock()
        tools.infra_type_search = search

        collector = OverridesCollector(
            defaults=defaults,
            tools=tools
        )

        result = collector.collect_overrides_for(variant)

        self.assertEqual({infra_type_var: infra_type_val}, result)

        search.search.assert_called_once_with(variant)


class TestFilesFetcher(TestCase):
    """Tests for :class:`FilesFetcher`.
    """

    def test_no_custom_featureset(self):
        """Checks that the default value is returned if the variant has no
        custom featureset file.
        """
        default = 'path'

        variant = Mock()

        search = Mock()
        search.search = Mock()
        search.search.return_value = None

        tools = Mock()
        tools.featureset_search = search

        fetcher = FilesFetcher(tools)

        result = fetcher.fetch_featureset(variant, default)

        self.assertEqual(default, result)

    def test_custom_featureset(self):
        """Checks that this generates the featureset file path from the
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

        fetcher = FilesFetcher(tools)

        result = fetcher.fetch_featureset(variant, 'unused')

        self.assertEqual(path, result)

        search.search.assert_called_once_with(variant)
        files.create_featureset.assert_called_once_with(fs)
        paths.create_featureset_path.assert_called_once_with(file)

    def test_no_custom_nodes(self):
        """Checks that the default value is returned if the variant has no
        custom nodes file.
        """
        default = 'path'

        variant = Mock()

        search = Mock()
        search.search = Mock()
        search.search.return_value = None

        tools = Mock()
        tools.nodes_search = search

        fetcher = FilesFetcher(tools)

        result = fetcher.fetch_nodes(variant, default)

        self.assertEqual(default, result)

    def test_custom_nodes(self):
        """Checks that this generates the nodes file path from the
        variant's variables.
        """
        nodes = 'ctrl1'
        file = 'some_file.yml'
        path = 'path/to/some_file.yml'

        variant = Mock()

        files = Mock()
        files.create_nodes = Mock()
        files.create_nodes.return_value = file

        paths = Mock()
        paths.create_nodes_path = Mock()
        paths.create_nodes_path.return_value = path

        search = Mock()
        search.search = Mock()
        search.search.return_value = ('var', nodes)

        tools = Mock()
        tools.quickstart_files = files
        tools.quickstart_paths = paths
        tools.nodes_search = search

        fetcher = FilesFetcher(tools)

        result = fetcher.fetch_nodes(variant, 'unused')

        self.assertEqual(path, result)

        search.search.assert_called_once_with(variant)
        files.create_nodes.assert_called_once_with(nodes)
        paths.create_nodes_path.assert_called_once_with(file)

    def test_no_custom_release(self):
        """Checks that the default value is returned if the variant as no
        custom release file.
        """
        default = 'path'

        variant = Mock()

        search = Mock()
        search.search = Mock()
        search.search.return_value = None

        tools = Mock()
        tools.release_search = search

        fetcher = FilesFetcher(tools)

        result = fetcher.fetch_release(variant, default)

        self.assertEqual(default, result)

    def test_custom_release(self):
        """Checks that this generates the release file path from the
        variant's variables.
        """
        release = 'master'
        file = 'some_file.yml'
        path = 'path/to/some_file.yml'

        variant = Mock()

        files = Mock()
        files.create_release = Mock()
        files.create_release.return_value = file

        paths = Mock()
        paths.create_release_path = Mock()
        paths.create_release_path.return_value = path

        search = Mock()
        search.search = Mock()
        search.search.return_value = ('var', release)

        tools = Mock()
        tools.quickstart_files = files
        tools.quickstart_paths = paths
        tools.release_search = search

        fetcher = FilesFetcher(tools)

        result = fetcher.fetch_release(variant, 'unused')

        self.assertEqual(path, result)

        search.search.assert_called_once_with(variant)
        files.create_release.assert_called_once_with(release)
        paths.create_release_path.assert_called_once_with(file)


class TestOutlineCreator(TestCase):
    """Tests for :class:`OutlineCreator`.
    """

    def test_fetches_featureset(self):
        """Checks that this will read the featureset file from the variant.
        Also, checks the default value it will use if there is no custom file
        in there.
        """
        featureset = 'some_value'

        variant = Mock()

        fetcher = Mock()
        fetcher.fetch_featureset = Mock()
        fetcher.fetch_featureset.return_value = featureset

        tools = Mock()
        tools.files_fetcher = fetcher

        creator = OutlineCreator(tools)

        result = creator.new_outline_for(variant)

        self.assertEqual(featureset, result.featureset)

        fetcher.fetch_featureset.assert_called_once_with(
            variant,
            DEFAULT_FEATURESET_FILE
        )

    def test_fetches_nodes(self):
        """Checks that this will read the nodes file from the variant. Also,
        checks the default value it will use if there is no custom file in
        there.
        """
        nodes = 'some_value'

        variant = Mock()

        fetcher = Mock()
        fetcher.fetch_nodes = Mock()
        fetcher.fetch_nodes.return_value = nodes

        tools = Mock()
        tools.files_fetcher = fetcher

        creator = OutlineCreator(tools)

        result = creator.new_outline_for(variant)

        self.assertEqual(nodes, result.nodes)

        fetcher.fetch_nodes.assert_called_once_with(
            variant,
            DEFAULT_NODES_FILE
        )

    def test_fetches_release(self):
        """Checks that this will read the release file from the variant.
        Also, checks the default value it will use if there is no custom
        file in there.
        """
        release = 'some_value'

        variant = Mock()

        fetcher = Mock()
        fetcher.fetch_release = Mock()
        fetcher.fetch_release.return_value = release

        tools = Mock()
        tools.files_fetcher = fetcher

        creator = OutlineCreator(tools)

        result = creator.new_outline_for(variant)

        self.assertEqual(release, result.release)

        fetcher.fetch_release.assert_called_once_with(
            variant,
            DEFAULT_RELEASE_FILE
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
