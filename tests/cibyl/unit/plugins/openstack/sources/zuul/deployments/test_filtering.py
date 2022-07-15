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

from cibyl.plugins.openstack.sources.zuul.deployments.filtering import \
    DeploymentFiltering


class TestDeploymentFiltering(TestCase):
    """Tests for :class:`DeploymentFiltering`.
    """

    def test_applies_release_filter(self):
        """Checks that the filter for releases is generated and applied.
        """
        release1 = '1'
        release2 = '2'

        release_arg = Mock()
        release_arg.value = [release1]

        kwargs = {
            'release': release_arg
        }

        deployment1 = Mock()
        deployment1.release.value = release1

        deployment2 = Mock()
        deployment2.release.value = release2

        filtering = DeploymentFiltering()
        filtering.add_filters_from(**kwargs)

        self.assertTrue(filtering.is_valid_deployment(deployment1))
        self.assertFalse(filtering.is_valid_deployment(deployment2))

    def test_applies_infra_type_filter(self):
        """Checks that the filter for infra type is generated and applied.
        """
        infra_type1 = 'ovb'
        infra_type2 = 'libvirt'

        infra_type_arg = Mock()
        infra_type_arg.value = [infra_type1]

        kwargs = {
            'infra_type': infra_type_arg
        }

        deployment1 = Mock()
        deployment1.infra_type.value = infra_type1

        deployment2 = Mock()
        deployment2.infra_type.value = infra_type2

        filtering = DeploymentFiltering()
        filtering.add_filters_from(**kwargs)

        self.assertTrue(filtering.is_valid_deployment(deployment1))
        self.assertFalse(filtering.is_valid_deployment(deployment2))

    def test_applies_topology_filter(self):
        """Checks that the filter for topology is generated and applied.
        """
        topology1 = 'ctrl1;'
        topology2 = 'ctrl2;'

        topology_arg = Mock()
        topology_arg.value = [topology1]

        kwargs = {
            'topology': topology_arg
        }

        deployment1 = Mock()
        deployment1.topology.value = topology1

        deployment2 = Mock()
        deployment2.topology.value = topology2

        filtering = DeploymentFiltering()
        filtering.add_filters_from(**kwargs)

        self.assertTrue(filtering.is_valid_deployment(deployment1))
        self.assertFalse(filtering.is_valid_deployment(deployment2))

    def test_applies_ip_version_filter(self):
        """Checks that the filter for ip version is generated and applied.
        """
        ip_version1 = 'ipv4'
        ip_version2 = 'ipv6'

        ip_version_arg = Mock()
        ip_version_arg.value = [ip_version1]

        kwargs = {
            'ip_version': ip_version_arg
        }

        deployment1 = Mock()
        deployment1.network.value.ip_version.value = ip_version1

        deployment2 = Mock()
        deployment2.network.value.ip_version.value = ip_version2

        filtering = DeploymentFiltering()
        filtering.add_filters_from(**kwargs)

        self.assertTrue(filtering.is_valid_deployment(deployment1))
        self.assertFalse(filtering.is_valid_deployment(deployment2))

    def test_applied_cinder_backend_filter(self):
        """Checks that the filter for cinder backend is generated and
        applied.
        """
        cinder_backend1 = 'iscsi'
        cinder_backend2 = 'rbd'

        cinder_backend_arg = Mock()
        cinder_backend_arg.value = [cinder_backend1]

        kwargs = {
            'cinder_backend': cinder_backend_arg
        }

        deployment1 = Mock()
        deployment1.storage.value.cinder_backend.value = cinder_backend1

        deployment2 = Mock()
        deployment2.storage.value.cinder_backend.value = cinder_backend2

        filtering = DeploymentFiltering()
        filtering.add_filters_from(**kwargs)

        self.assertTrue(filtering.is_valid_deployment(deployment1))
        self.assertFalse(filtering.is_valid_deployment(deployment2))
