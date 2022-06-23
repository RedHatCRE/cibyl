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

from cibyl.outputs.cli.ci.system.utils.sorting.builds import SortBuildsByUUID


class TestSortBuildsByUUID(TestCase):
    """Tests for :class:`SortBuildsByUUID`.
    """

    def test_uuids_are_equal(self):
        """Checks that two builds are equal if they share the same uuid.
        """
        build1 = Mock()
        build1.build_id.value = '0'

        build2 = Mock()
        build2.build_id.value = '0'

        comparator = SortBuildsByUUID()

        self.assertEqual(
            0,
            comparator.compare(build1, build2)
        )

    def test_chronological_order(self):
        """Checks that the comparator will sort builds in chronological order.
        """
        build1 = Mock()
        build1.build_id.value = '9'

        build2 = Mock()
        build2.build_id.value = '10'

        comparator = SortBuildsByUUID()

        self.assertEqual(
            -1,
            comparator.compare(build1, build2)
        )

        self.assertEqual(
            1,
            comparator.compare(build2, build1)
        )
