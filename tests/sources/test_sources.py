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
from unittest.mock import Mock, patch, call

from cibyl.exceptions.source import TooManyValidSources
from cibyl.sources.source import Source


class TestGetSourceMethod(TestCase):
    """Tests for the get_source_method static function."""

    @patch('cibyl.sources.source.Source.is_source_valid')
    def test_no_more_than_two_valid_sources_allowed(self, valid_source):
        """Checks that only a single source is allowed to provide the
        desired function.

        :param valid_source: Mock for "is_source_valid"
        :type valid_source: :class:`Mock`
        """
        desired_func = 'func'

        source1 = Mock()
        source2 = Mock()

        valid_source.return_value = True

        with self.assertRaises(TooManyValidSources):
            Source.get_source_method(
                'system',
                [source1, source2],
                desired_func
            )

        valid_source.assert_has_calls([
            call(source1, desired_func),
            call(source2, desired_func)
        ])
