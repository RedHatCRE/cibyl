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

from cibyl.plugins.openstack.sources.zuul.deployments.summary import \
    VariantDeployment


class TestVariantDeployment(TestCase):
    """Tests for :class:`VariantDeployment`.
    """

    def setUp(self):
        self.variant = Mock()
        self.summary = Mock()

        self.outlines = Mock()
        self.lookup = Mock()
        self.release = Mock()

        self.lookup.run = Mock()
        self.lookup.run.return_value = self.summary

        self.tools = Mock()
        self.tools.outline_creator = self.outlines
        self.tools.deployment_lookup = self.lookup
        self.tools.release_search = self.release

    def test_get_default_release(self):
        """Checks that a default value is returned if the release is not
        present on the variant.
        """
        self.release.search = Mock()
        self.release.search.return_value = None

        deployment = VariantDeployment(self.variant, tools=self.tools)

        self.assertEqual('master', deployment.get_release())

    def test_get_release(self):
        """Checks that the release from the search is returned if it is
        present.
        """
        value = 'release'

        self.release.search = Mock()
        self.release.search.return_value = ('', value)

        deployment = VariantDeployment(self.variant, tools=self.tools)

        self.assertEqual(value, deployment.get_release())

        self.release.search.assert_called_with(self.variant)

    def test_get_nodes(self):
        """Checks that the nodes are returned as a list.
        """
        role = 'role'

        node = Mock()
        node.name = 'node'

        nodes = Mock()
        nodes._asdict = Mock()
        nodes._asdict.return_value = Mock()
        nodes._asdict.return_value.items = Mock()
        nodes._asdict.return_value.items.return_value = ((role, (node,)),)

        topology = Mock()
        topology.nodes = nodes

        self.summary.topology = topology

        deployment = VariantDeployment(self.variant, tools=self.tools)

        result = deployment.get_nodes()

        self.assertIsNotNone(result)
        self.assertEqual(1, len(result))
        self.assertEqual(role, result[0].role.value)
        self.assertEqual(node.name, result[0].name.value)

    def test_get_topology(self):
        """Checks that the topology is returned as a string.
        """
        value = 'topology'

        topology = Mock()
        topology.__str__ = Mock()
        topology.__str__.return_value = value

        self.summary.topology = topology

        deployment = VariantDeployment(self.variant, tools=self.tools)

        self.assertEqual(value, deployment.get_topology())
