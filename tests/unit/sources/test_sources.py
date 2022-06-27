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
from unittest.mock import Mock, patch

from cibyl.exceptions.source import NoSupportedSourcesFound, NoValidSources
from cibyl.sources.source import (Source, get_source_instance_from_method,
                                  get_source_method, is_source_valid,
                                  select_source_method,
                                  source_information_from_method)
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
        self.assertEqual(score, 4)
        method, score = sources_out[1]
        self.assertEqual(method.__self__.name, "jenkins")
        self.assertEqual(score, 1)

    def test_get_source_no_valid_sources(self):
        """Test that get_source_method raises an exceptions with no valid
        source."""
        msg = """Couldn't find any enabled source for the system test_system
         that implements the function get_builds.""""".replace("\n", " ")
        with self.assertRaises(NoSupportedSourcesFound, msg=msg):
            get_source_method("test_system", [], "get_builds", {})

    @patch("cibyl.sources.source.get_source_method")
    def test_select_source(self, patched_method):
        """Testing select_source_method function"""
        system = Mock()
        system.name = Mock()
        system.name.value = "system"
        system.sources = Mock()
        source = Mock()
        source.name = "jenkins"
        system.sources = [source]
        argument = Mock()
        argument.func = None
        select_source_method(system, None)
        patched_method.assert_called_with(
            "system", [source], None, args={})

    def test_select_source_invalid_source(self):
        """Testing select_source_method function with no valid
        source.
        """
        system = Mock()
        system.name = Mock()
        system.name.value = "system"
        system.sources = Mock()
        system.sources = []
        argument = Mock()
        argument.func = None
        self.assertRaises(NoValidSources,
                          select_source_method,
                          system, "")

    def test_source_information_from_method(self):
        """Test that the source_information_from_method methods provides the
        correct representation of the source."""
        source = Source(name="source", driver="driver")
        expected = "source: 'source' of type: 'driver'"
        output = source_information_from_method(source.setup)
        self.assertEqual(expected, output)


class TestGetSourceInstanceFromMethod(TestCase):
    """Test the get_source_instance_from_method function from source module."""
    def test_get_source_methods_get_builds(self):
        """Test that get_source_method returns the correct ordering after
        asking for get_builds method."""
        source = SourceFactory.create_source("zuul", "zuul", url="url")

        source_out = get_source_instance_from_method(source.get_builds)

        self.assertTrue(source_out, source)


class TestSourceSetup(TestCase):
    """Test that setup functionality for Source class."""
    def setUp(self):
        self.source = Source()

    def test_default_setup_false(self):
        """Test that is_setup return False by default."""
        self.assertFalse(self.source.is_setup())

    def test_setup(self):
        """Test that ensure_source_setup calls setup and sets the right value
        for _setup attribute."""
        self.source.ensure_source_setup()
        self.assertTrue(self.source.is_setup())

    def test_setup_multiple_calls(self):
        """Test that multiple calls to ensure_source_setup calls setup
        just once and sets the right value for _setup attribute."""
        self.source.ensure_source_setup()
        self.source.ensure_source_setup()
        self.source.ensure_source_setup()
        self.assertTrue(self.source.is_setup())


class TestSourceTearDown(TestCase):
    """Test that teardown functionality for Source class."""
    def setUp(self):
        self.source = Source()

    def test_default_down_false(self):
        """Test that is_down return False by default."""
        self.assertFalse(self.source.is_down())

    def test_teardown(self):
        """Test that ensure_teardown call teardown and sets the right value
        for _down attribute."""
        self.source.ensure_source_setup()
        self.assertTrue(self.source.is_setup())
        self.source.ensure_teardown()
        self.assertTrue(self.source.is_down())

    def test_down_multiple_calls(self):
        """Test that multiple calls to ensure_teardown calls setup
        just once and sets the right value for _down attribute."""
        self.source.ensure_source_setup()
        self.assertTrue(self.source.is_setup())
        self.source.ensure_teardown()
        self.source.ensure_teardown()
        self.source.ensure_teardown()
        self.assertTrue(self.source.is_down())
