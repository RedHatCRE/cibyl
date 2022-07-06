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

from cibyl.plugins.openstack.sources.zuul.deployments.outlines import \
    OutlineCreator
from tripleo.insights.defaults import DEFAULT_FEATURESET_FILE


class TestOutlineCreator(TestCase):
    """Tests for :class:`OutlineCreator`.
    """

    def test_outline_no_path_for_featureset(self):
        """Checks that the default featureset is used if the variant has no
        custom featureset.
        """
        variant = Mock()

        search = Mock()
        search.search = Mock()
        search.search.return_value = ('var', None)

        tools = Mock()
        tools.featureset_search = search

        creator = OutlineCreator(tools)

        result = creator.new_outline_for(variant)

        self.assertEqual(DEFAULT_FEATURESET_FILE, result.featureset)

    def test_outline_has_path_for_featureset(self):
        """Checks that the factory generates the featureset path from the
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

        creator = OutlineCreator(tools)

        result = creator.new_outline_for(variant)

        self.assertEqual(path, result.featureset)

        search.search.assert_called_once_with(variant)
        files.create_featureset.assert_called_once_with(fs)
        paths.create_featureset_path.assert_called_once_with(file)
