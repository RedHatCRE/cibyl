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

from cibyl.plugins.openstack.sources.zuul.deployments.generator import \
    DeploymentGenerator


class TestDeploymentGenerator(TestCase):
    """Tests for :class:`DeploymentGenerator`.
    """

    def setUp(self):
        self.arguments = Mock()
        self.arguments.is_nodes_requested.return_value = False

        self.summary = Mock()

        self.summaries = Mock()
        self.summaries.create_for = Mock()
        self.summaries.create_for.return_value = self.summary

        self.tools = Mock()
        self.tools.argument_review = self.arguments
        self.tools.variant_summary = self.summaries

    def test_no_release(self):
        """Checks that the release is ignored if it is not requested.
        """
        kwargs = {'key': 'val'}
        variant = Mock()

        self.arguments.is_release_requested = Mock()
        self.arguments.is_release_requested.return_value = False

        generator = DeploymentGenerator(tools=self.tools)

        result = generator.generate_deployment_for(variant, **kwargs)

        self.assertEqual(None, result.release.value)

        self.arguments.is_release_requested.assert_called_once_with(**kwargs)

    def test_no_infra_type(self):
        """Checks that the infra type is ignored if it is not requested.
        """
        kwargs = {'key': 'val'}
        variant = Mock()

        self.arguments.is_infra_type_requested = Mock()
        self.arguments.is_infra_type_requested.return_value = False

        generator = DeploymentGenerator(tools=self.tools)

        result = generator.generate_deployment_for(variant, **kwargs)

        self.assertEqual(None, result.infra_type.value)

        self.arguments.is_infra_type_requested \
            .assert_called_once_with(**kwargs)

    def test_no_nodes(self):
        """Checks that the nodes are ignored if it is not requested.
        """
        kwargs = {'key': 'val'}
        variant = Mock()

        self.arguments.is_nodes_requested = Mock()
        self.arguments.is_nodes_requested.return_value = False

        generator = DeploymentGenerator(tools=self.tools)

        result = generator.generate_deployment_for(variant, **kwargs)

        self.assertEqual({}, result.nodes.value)

        self.arguments.is_nodes_requested.assert_called_once_with(**kwargs)

    def test_no_topology(self):
        """Checks that the topology is ignored if it is not requested.
        """
        kwargs = {'key': 'val'}
        variant = Mock()

        self.arguments.is_topology_requested = Mock()
        self.arguments.is_topology_requested.return_value = False

        generator = DeploymentGenerator(tools=self.tools)

        result = generator.generate_deployment_for(variant, **kwargs)

        self.assertEqual(None, result.topology.value)

        self.arguments.is_topology_requested.assert_called_once_with(**kwargs)

    def test_no_cinder_backend(self):
        """Checks that the cinder backend is ignored if it is not requested.
        """
        kwargs = {'key': 'val'}
        variant = Mock()

        self.arguments.is_cinder_backend_requested = Mock()
        self.arguments.is_cinder_backend_requested.return_value = False

        generator = DeploymentGenerator(tools=self.tools)

        result = generator.generate_deployment_for(variant, **kwargs)

        self.assertEqual(None, result.storage.value.cinder_backend.value)

        self.arguments.is_cinder_backend_requested \
            .assert_called_once_with(**kwargs)

    def test_no_ip_version(self):
        """Checks that the ip version is ignored if it is not requested.
        """
        kwargs = {'key': 'val'}
        variant = Mock()

        self.arguments.is_ip_version_requested = Mock()
        self.arguments.is_ip_version_requested.return_value = False

        generator = DeploymentGenerator(tools=self.tools)

        result = generator.generate_deployment_for(variant, **kwargs)

        self.assertEqual(None, result.network.value.ip_version.value)

        self.arguments.is_ip_version_requested \
            .assert_called_once_with(**kwargs)

    def test_release(self):
        """Checks that the release is returned if requested.
        """
        value = 'release'

        variant = Mock()

        self.arguments.is_release_requested = Mock()
        self.arguments.is_release_requested.return_value = True

        self.summary.get_release = Mock()
        self.summary.get_release.return_value = value

        generator = DeploymentGenerator(tools=self.tools)

        result = generator.generate_deployment_for(variant)

        self.assertEqual(value, result.release.value)

        self.summaries.create_for.assert_called_once_with(variant)
        self.summary.get_release.assert_called_once()

    def test_infra_type(self):
        """Checks that the infra type is returned if requested.
        """
        value = 'infra_type'

        variant = Mock()

        self.arguments.is_infra_type_requested = Mock()
        self.arguments.is_infra_type_requested.return_value = True

        self.summary.get_infra_type = Mock()
        self.summary.get_infra_type.return_value = value

        generator = DeploymentGenerator(tools=self.tools)

        result = generator.generate_deployment_for(variant)

        self.assertEqual(value, result.infra_type.value)

        self.summaries.create_for.assert_called_once_with(variant)
        self.summary.get_infra_type.assert_called_once()

    def test_nodes(self):
        """Checks that the nodes are returned if requested.
        """
        node = Mock()
        node.name.value = 'node'

        variant = Mock()

        self.arguments.is_nodes_requested = Mock()
        self.arguments.is_nodes_requested.return_value = True

        self.summary.get_nodes = Mock()

        generator = DeploymentGenerator(tools=self.tools)

        self.summary.get_nodes.return_value = None

        self.assertEqual(
            {},
            generator.generate_deployment_for(variant).nodes.value
        )

        self.summary.get_nodes.return_value = (node,)

        self.assertEqual(
            {node.name.value: node},
            generator.generate_deployment_for(variant).nodes.value
        )

    def test_topology(self):
        """Checks that the topology is returned if requested.
        """
        value = 'topology'

        variant = Mock()

        self.arguments.is_topology_requested = Mock()
        self.arguments.is_topology_requested.return_value = True

        self.summary.get_topology = Mock()
        self.summary.get_topology.return_value = value

        generator = DeploymentGenerator(tools=self.tools)

        result = generator.generate_deployment_for(variant)

        self.assertEqual(value, result.topology.value)

        self.summaries.create_for.assert_called_once_with(variant)
        self.summary.get_topology.assert_called_once()

    def test_cinder_backend(self):
        """Checks that the cinder backend is returned if requested.
        """
        value = 'cinder_backend'

        variant = Mock()

        self.arguments.is_cinder_backend_requested = Mock()
        self.arguments.is_cinder_backend_requested.return_value = True

        self.summary.get_cinder_backend = Mock()
        self.summary.get_cinder_backend.return_value = value

        generator = DeploymentGenerator(tools=self.tools)

        result = generator.generate_deployment_for(variant)

        self.assertEqual(value, result.storage.value.cinder_backend.value)

        self.summaries.create_for.assert_called_once_with(variant)
        self.summary.get_cinder_backend.assert_called_once()

    def test_ip_version(self):
        """Checks that the ip version is returned if requested.
        """
        value = 'release'

        variant = Mock()

        self.arguments.is_ip_version_requested = Mock()
        self.arguments.is_ip_version_requested.return_value = True

        self.summary.get_ip_version = Mock()
        self.summary.get_ip_version.return_value = value

        generator = DeploymentGenerator(tools=self.tools)

        result = generator.generate_deployment_for(variant)

        self.assertEqual(value, result.network.value.ip_version.value)

        self.summaries.create_for.assert_called_once_with(variant)
        self.summary.get_ip_version.assert_called_once()

    def test_tls_everywhere(self):
        """Checks that TLS-Everywhere is returned if requested.
        """
        value = 'tls-everywhere'

        variant = Mock()

        self.arguments.is_tls_everywhere_requested = Mock()
        self.arguments.is_tls_everywhere_requested.return_value = True

        self.summary.get_tls_everywhere = Mock()
        self.summary.get_tls_everywhere.return_value = value

        generator = DeploymentGenerator(tools=self.tools)

        result = generator.generate_deployment_for(variant)

        self.assertEqual(value, result.network.value.tls_everywhere.value)

        self.summaries.create_for.assert_called_once_with(variant)
        self.summary.get_tls_everywhere.assert_called_once()
