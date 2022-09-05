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

from cibyl.sources.zuul.output import QueryOutputMode
from cibyl.sources.zuul.queries.composition.factory import \
    AggregatedQueryFactory
from cibyl.sources.zuul.queries.composition.quick import QuickQuery
from cibyl.sources.zuul.queries.composition.verbose import VerboseQuery

pkg = 'cibyl.sources.zuul.queries.composition.factory'


class TestAggregatedQueryFactory(TestCase):
    """Tests for :class:`AggregatedQueryFactory`.
    """

    def test_defaults_to_quick_if_no_arg(self):
        """Checks that if the mode is not specified then the quick query is
        returned.
        """
        api = Mock()

        query = AggregatedQueryFactory()

        result = query.from_kwargs(api)

        self.assertIsInstance(result, QuickQuery)

    @patch(f'{pkg}.QueryOutputMode.from_key')
    def test_defaults_to_quick_if_unknown(self, parser: Mock):
        """Checks that if the mode is unknown then the quick query is
        returned.
        """
        api = Mock()
        arg = 'unknown'

        parser.return_value = 10

        query = AggregatedQueryFactory()

        result = query.from_kwargs(api, **{'mode': arg})

        self.assertIsInstance(result, QuickQuery)

        parser.assert_called_once_with(arg)

    @patch(f'{pkg}.QueryOutputMode.from_key')
    def test_quick_mode(self, parser: Mock):
        """Checks that quick mode is returned if the argument specifies so.
        """
        api = Mock()
        arg = 'normal'

        parser.return_value = QueryOutputMode.NORMAL

        query = AggregatedQueryFactory()

        result = query.from_kwargs(api, **{'mode': arg})

        self.assertIsInstance(result, QuickQuery)

        parser.assert_called_once_with(arg)

    @patch(f'{pkg}.QueryOutputMode.from_key')
    def test_verbose_mode(self, parser: Mock):
        """Checks that verbose mode is returned if the argument specifies so.
        """
        api = Mock()
        arg = 'verbose'

        parser.return_value = QueryOutputMode.VERBOSE

        query = AggregatedQueryFactory()

        result = query.from_kwargs(api, **{'mode': arg})

        self.assertIsInstance(result, VerboseQuery)

        parser.assert_called_once_with(arg)
