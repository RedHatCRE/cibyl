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

from tripleo.insights.topology import Node, Topology


class TestTopology(TestCase):
    """Tests for :class:`Topology`.
    """

    def test_full_str(self):
        """Checks the output of __str__ if all elements have values.
        """
        topology = Topology(
            nodes=Topology.Nodes(
                compute=(
                    Node('compute_1'),
                    Node('compute_2'),
                    Node('compute_3')
                ),
                controller=(
                    Node('ctrl_1'),
                    Node('ctrl_2')
                ),
                ceph=(
                    Node('ceph_1')
                )
            )
        )

        self.assertEqual(
            'compute:3,controller:2,ceph:1',
            str(topology)
        )

    def test_partial_str(self):
        """Checks that items set to 0 do not take part on the __str__
        output.
        """
        topology = Topology(
            nodes=Topology.Nodes(
                compute=(
                    Node('compute_1'),
                    Node('compute_2')
                ),
                ceph=(
                    Node('ceph_1')
                )
            )
        )

        self.assertEqual(
            'compute:2,ceph:1',
            str(topology)
        )
