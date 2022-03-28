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

from cibyl.utils.filtering import apply_filters


class TestApplyFilters(TestCase):
    def test_filters_are_applied(self):
        data = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

        filters = [
            lambda number: number >= 5,
            lambda number: number <= 5
        ]

        self.assertEqual([5], apply_filters(data, *filters))
