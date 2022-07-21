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
from typing import Iterable, NamedTuple


class Node(NamedTuple):
    """A node on the topology.
    """
    name: str
    """The node's name."""

    def __eq__(self, other):
        if self is other:
            return True

        if not isinstance(other, Node):
            return False

        return self.name == other.name


class Topology(NamedTuple):
    """Description of the deployment's topology.
    """

    class Nodes(NamedTuple):
        """Contains all the nodes that form part of the topology, divided by
        type.
        """
        compute: Iterable[Node] = ()
        """Collection holding all the compute nodes."""
        controller: Iterable[Node] = ()
        """Collection holding all the controller nodes."""
        ceph: Iterable[Node] = ()
        """Collection holding all the ceph nodes."""

        def __eq__(self, other):
            if self is other:
                return True

            if not isinstance(other, Topology.Nodes):
                return False

            # Casting to tuple as containers do not have to be of same type
            return \
                tuple(self.compute) == tuple(other.compute) and \
                tuple(self.controller) == tuple(other.controller) and \
                tuple(self.ceph) == tuple(other.ceph)

    # By default, all instances will share an empty immutable collection
    nodes: Nodes = Nodes()
    """Nodes on the topology."""

    def __eq__(self, other):
        if self is other:
            return True

        if not isinstance(other, Topology):
            return False

        return self.nodes == other.nodes

    def __str__(self):
        result = ''

        for node_type, nodes in self.nodes._asdict().items():
            # Ignore if there are no nodes of this type
            if not nodes:
                continue

            # If not the first element, add a separator
            if result:
                result += ','

            result += f'{node_type}:{len(nodes)}'

        return result
