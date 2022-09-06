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

from cibyl.sources.zuul.queries.composition.factory import \
    AggregatedQueryFactory
from cibyl.sources.zuul.queries.composition.quick import QuickQuery
from cibyl.sources.zuul.queries.composition.verbose import VerboseQuery


class TestAggregatedQueryFactory(TestCase):
    """Tests for :class:`AggregatedQueryFactory`.
    """

    def test_verbose_query(self):
        """Checks conditions that make the verbose query be returned.
        """
        factory = AggregatedQueryFactory()

        self.assertIsInstance(
            factory.from_kwargs(
                api=Mock(),
                **{'fetch_pipelines': None}
            ),
            VerboseQuery
        )

    def test_quick_query(self):
        """Checks conditions that make the quick query be returned.
        """
        factory = AggregatedQueryFactory()

        self.assertIsInstance(
            factory.from_kwargs(
                api=Mock(),
                **{}
            ),
            QuickQuery
        )
