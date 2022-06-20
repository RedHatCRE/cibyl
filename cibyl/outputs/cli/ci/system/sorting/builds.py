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
from cibyl.utils.sorting import Comparator


class SortBuildsByUUID(Comparator):
    """Sorts builds in alphabetical order based on their uuid.
    """

    def compare(self, left, right):
        """See parent function for more information.

        :type left: :class:`cibyl.models.ci.base.build.Build`
        :type right: :class:`cibyl.models.ci.base.build.Build`
        """
        uuid_left = left.build_id.value.lower()
        uuid_right = right.build_id.value.lower()

        if uuid_left == uuid_right:
            return 0

        return -1 if uuid_left < uuid_right else 1
