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

import cibyl
from cibyl.exceptions.source import TooManyValidSources
from cibyl.sources.source import get_source_method, is_source_valid


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
    """Tests for the get_source_method static function."""

    def test_no_more_than_two_valid_sources_allowed(self):
        """Checks that only a single source is allowed to provide the
        desired function.
        """
        func = 'func'

        source1 = Mock()
        source2 = Mock()

        validity_check = cibyl.sources.source.is_source_valid = Mock()
        validity_check.return_value = True

        with self.assertRaises(TooManyValidSources):
            get_source_method('system', [source1, source2], func)

        validity_check.assert_has_calls([
            call(source1, func),
            call(source2, func)
        ])
