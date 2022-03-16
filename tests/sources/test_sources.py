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

from cibyl.exceptions.source import TooManyValidSources
from cibyl.sources.source import Source


class TestGetSourceMethod(TestCase):
    """Tests for the get_source_method static function."""

    def test_no_more_than_two_valid_sources_allowed(self):
        """Checks that only a single source is allowed to provide the
        desired function.
        """
        source1 = Mock()
        source2 = Mock()

        source1.func = Mock()
        source2.func = Mock()

        self.assertRaises(
            TooManyValidSources,
            Source.get_source_method,
            'system',
            [source1, source2],
            'func'
        )
