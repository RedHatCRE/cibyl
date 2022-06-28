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

from cibyl.outputs.cli.ci.system.utils.sorting.jobs import SortJobsByName


class TestSortJobsByName(TestCase):
    """Tests for :class:`SortJobsByName`.
    """

    def test_names_are_equal(self):
        """Checks that two jobs are equal if they share the same name.
        """
        job1 = Mock()
        job1.name.value = 'job'

        job2 = Mock()
        job2.name.value = 'job'

        comparator = SortJobsByName()

        self.assertEqual(
            0,
            comparator.compare(job1, job2)
        )

    def test_alphabetical_order(self):
        """Checks that the comparator will sort jobs in alphabetical order.
        """
        job1 = Mock()
        job1.name.value = 'A'

        job2 = Mock()
        job2.name.value = 'B'

        comparator = SortJobsByName()

        self.assertEqual(
            -1,
            comparator.compare(job1, job2)
        )

        self.assertEqual(
            1,
            comparator.compare(job2, job1)
        )
