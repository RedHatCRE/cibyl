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

from cibyl.exceptions.source import NoSupportedSourcesFound
from cibyl.sources.source import get_source_method, is_source_valid
from cibyl.sources.source_factory import SourceFactory


class TestIsSourceValid(TestCase):
    """Test for the is_source_valid static function."""

    def test_invalid_if_disabled(self):
        """Checks that a source is not valid is not enabled.
        """
        source = Mock()

        source.enabled = False

        self.assertFalse(is_source_valid(source, 'func'))

    def test_invalid_if_no_desired_attribute(self):
        """Checks that a source is invalid if it does not present the
        desired attribute.
        """
        source = Mock()

        source.enabled = True
        del source.func

        self.assertFalse(is_source_valid(source, 'func'))

    def test_valid_if_meets_all_requirements(self):
        """Checks that a source can be considered valid if it meets all
        requirements.
        """
        source = Mock()

        source.enabled = True
        source.func = Mock()

        self.assertTrue(is_source_valid(source, 'func'))


class TestGetSourceMethod(TestCase):
    """Test the get_source_method function from source module."""
    def test_get_source_methods_get_builds(self):
        """Test that get_source_method returns the correct ordering after
        asking for get_builds method."""
        sources = [SourceFactory.create_source("zuul", "zuul", url="url"),
                   SourceFactory.create_source("jenkins", "jenkins",
                                               url="url")]

        sources_out = get_source_method("test_system", sources, "get_builds",
                                        {})

        # get_source_method returns tuples of (source, speed index)
        method, score = sources_out[0]
        self.assertEqual(method.__self__.name, "zuul")
        self.assertEqual(score, 3)
        method, score = sources_out[1]
        self.assertEqual(method.__self__.name, "jenkins")
        self.assertEqual(score, 1)

    def test_get_source_no_valid_sources(self):
        """Test that get_source_method raises an exceptions with no valid
        source."""
        self.assertRaises(NoSupportedSourcesFound, get_source_method,
                          "test_system", [], "get_builds", {})
