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
from cibyl.models.ci.base.build import Build
from cibyl.utils.sorting import Comparator


class SortBuildsByUUID(Comparator):
    """Sorts builds in alphabetical order based on their uuid.
    """

    def compare(self, left: Build, right: Build) -> int:
        """See parent function for more information."""
        uuid_left = left.build_id.value.lower()
        uuid_right = right.build_id.value.lower()

        if uuid_left == uuid_right:
            return 0

        # If IDs are numbers, compare as so. Otherwise, compare as strings.
        if uuid_left.isnumeric() and uuid_right.isnumeric():
            uuid_left = int(uuid_left)
            uuid_right = int(uuid_right)

        return -1 if uuid_left < uuid_right else 1
