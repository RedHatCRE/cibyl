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
from dataclasses import dataclass, fields


@dataclass
class Topology:
    """Description of the deployment's topology.
    """
    compute: int = 0
    """Number of compute nodes."""
    controller: int = 0
    """Number of controller nodes."""
    ceph: int = 0
    """Number of ceph nodes."""
    cell: int = 0
    """Number of cell nodes."""

    def __str__(self):
        result = ''

        for item in fields(type(self)):
            name = item.name
            value = getattr(self, name)

            # Ignore if there are no nodes of this type
            if not value:
                continue

            # If not the first element, add a separator
            if result:
                result += ','

            result += f'{name}:{value}'

        return result
