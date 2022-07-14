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
from cibyl.models.ci.base.job import Job
from cibyl.utils.sorting import Comparator


class SortJobsByName(Comparator):
    """Sorts jobs in alphabetical order based on their name.
    """

    def compare(self, left: Job, right: Job) -> int:
        """See parent function for more information."""
        name_left = left.name.value.lower()
        name_right = right.name.value.lower()

        if name_left == name_right:
            return 0

        return -1 if name_left < name_right else 1
