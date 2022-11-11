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

from cibyl.sources.zuul.source import Zuul
from kernel.tools.dicts import nsubset


class TestFallbacks(TestCase):
    """Tests for :class:`Zuul.Fallbacks`.
    """

    def test_from_kwargs(self):
        """Checks that the fallbacks are created properly from the keyword
        arguments.
        """
        data = {
            'key1': ['val1'],
            'key2': 'val2',
            'key3': 'val3'
        }

        fallbacks = Zuul.Fallbacks.from_kwargs(
            keys=['key1', 'key2', 'key4'],
            **data
        )

        self.assertEqual(
            nsubset(data, ['key3']),
            fallbacks
        )
