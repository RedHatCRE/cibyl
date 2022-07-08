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

from cibyl.plugins.openstack.sources.zuul.deployments.formatting import \
    TopologyPrinter


class TestTopologyPrinter(TestCase):
    """Tests for :class:`TopologyPrinter`.
    """

    def test_default_template(self):
        """Test the default format this class outputs in.
        """
        model = Mock()
        model.compute = 2
        model.ctrl = 1
        model.ceph = 4
        model.cell = 3

        printer = TopologyPrinter()

        self.assertEqual(
            'compute:2,controller:1,ceph:4,cell:3',
            printer.print(model)
        )
