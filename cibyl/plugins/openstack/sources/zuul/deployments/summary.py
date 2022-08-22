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
from dataclasses import dataclass
from typing import Iterable, Optional

from cached_property import cached_property

from cibyl.plugins.openstack.node import Node
from cibyl.plugins.openstack.sources.zuul.deployments.outlines import \
    OutlineCreator
from cibyl.plugins.openstack.sources.zuul.variants import ReleaseSearch
from cibyl.sources.zuul.transactions import VariantResponse as Variant
from tripleo.insights import DeploymentLookUp, DeploymentSummary


class VariantDeployment:
    """Extracts data related to the deployment of a variant.
    """

    @dataclass
    class Tools:
        """The tools this uses to do its task.
        """
        outline_creator = OutlineCreator()
        """Tests care of creating the TripleO outline for a Zuul job."""
        deployment_lookup = DeploymentLookUp()
        """Gets additional information on the deployment from TripleO."""
        release_search = ReleaseSearch()
        """Takes care of finding the release of the deployment."""

    def __init__(self, variant: Variant, tools: Tools = Tools()):
        """Constructor.

        :param variant: The variant to get the deployment for.
        :param tools: The tools this uses to do its task.
        """
        self._variant = variant
        self._tools = tools

    @property
    def variant(self) -> Variant:
        """
        :return: The variant to get the deployment for.
        """
        return self._variant

    @property
    def tools(self) -> Tools:
        """
        :return: The tools this uses to do its task.
        """
        return self._tools

    @cached_property
    def _summary(self) -> DeploymentSummary:
        """
        :return: All the deployment data that could be extracted from the
            variant. Being a cached property, the host will only be queries
            once, so feel free to call this as much as desired.
        """
        return self.tools.deployment_lookup.run(
            self.tools.outline_creator.new_outline_for(
                self.variant
            )
        )

    def get_release(self) -> Optional[str]:
        """
        :return: The RHOS release of the deployment. 'None' if it is not
            defined.
        """
        release = self.tools.release_search.search(self.variant)

        if not release:
            # No release defined -> Fall back to the default one
            return 'master'

        # Release defined -> Return its name
        _, value = release

        return value

    def get_infra_type(self) -> Optional[str]:
        """
        :return: Type of infrastructure used by the cloud. 'None' if it is
            not defined.
        """
        return self._summary.infra_type

    def get_nodes(self) -> Optional[Iterable[Node]]:
        """
        :return: Collection of nodes that form the topology. 'None' is they
            were not defined.
        """
        topology = self._summary.topology

        if not topology:
            return None

        result = []

        # Call to private function is allowed on named tuples
        for role, nodes in topology.nodes._asdict().items():
            for node in nodes:
                result.append(Node(name=node.name, role=role))

        return result

    def get_topology(self) -> Optional[str]:
        """
        :return: Description of the topology of the deployment. 'None' if it
            is not defined.
        """
        return str(self._summary.topology)

    def get_ip_version(self) -> Optional[str]:
        """
        :return: Number of the IP version used by the cloud. 'None' if it is
            not defined.
        """
        return self._summary.components.neutron.ip_version

    def get_neutron_backend(self) -> Optional[str]:
        """
        :return: Name of the backend that supports the Neutron component.
            'None' if it is not defined.
        """
        return self._summary.components.neutron.backend

    def get_tls_everywhere(self) -> Optional[str]:
        """
        :return: State of TLS-Everywhere on the deployment. 'None' if it is
            not defined.
        """
        return self._summary.components.neutron.tls_everywhere

    def get_ml2_driver(self) -> Optional[str]:
        """
        :return: Comma delimited list with all the ml2 drivers in use.
            'None' if it not defined.
        """
        return self._summary.components.neutron.ml2_driver

    def get_cinder_backend(self) -> Optional[str]:
        """
        :return: Name of the backend that supports the Cinder component.
            'None' if it is not defined.
        """
        return self._summary.components.cinder.backend


class VariantDeploymentFactory:
    """Builds instances of :class:`VariantDeployment`.
    """

    def create_for(self, variant: Variant) -> VariantDeployment:
        """
        :param variant: The variant to get the deployment for.
        :return: A new instance.
        """
        return VariantDeployment(variant)
