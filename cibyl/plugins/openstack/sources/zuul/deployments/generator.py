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
from typing import Any, Dict, Optional

from cibyl.plugins.openstack import Deployment
from cibyl.plugins.openstack.network import Network
from cibyl.plugins.openstack.node import Node
from cibyl.plugins.openstack.sources.zuul.deployments.arguments import \
    ArgumentReview
from cibyl.plugins.openstack.sources.zuul.deployments.summary import (
    VariantDeployment, VariantDeploymentFactory)
from cibyl.plugins.openstack.storage import Storage
from cibyl.sources.zuul.transactions import VariantResponse as Variant


class DeploymentGenerator:
    """Factory for generation of :class:`Deployment`.
    """

    @dataclass
    class Tools:
        """Tools the factory will use to do its task.
        """
        argument_review = ArgumentReview()
        """Used to understand what the user desires."""
        variant_summary = VariantDeploymentFactory()
        """Used to get data on a variant's deployment."""

    def __init__(self, tools: Tools = Tools()):
        """Constructor.

        :param tools: The tools this will use.
        """
        self._tools = tools

    @property
    def tools(self) -> Tools:
        """
        :return: The tools this will use.
        """
        return self._tools

    def generate_deployment_for(
        self,
        variant: Variant,
        **kwargs: Any
    ) -> Deployment:
        """Creates a new deployment based on the data from a job's variant.

        :param variant: The variant to fetch data from.
        :return: The deployment.
        """
        summary = self.tools.variant_summary.create_for(variant)

        return Deployment(
            release=self._get_release(summary, **kwargs),
            infra_type=self._get_infra_type(summary, **kwargs),
            nodes=self._get_nodes(summary, **kwargs),
            topology=self._get_topology(summary, **kwargs),
            network=Network(
                ip_version=self._get_ip_version(summary, **kwargs),
                network_backend=self._get_neutron_backend(summary, **kwargs),
                tls_everywhere=self._get_tls_everywhere(summary, **kwargs),
                ml2_driver=self._get_ml2_driver(summary, **kwargs)
            ),
            storage=Storage(
                cinder_backend=self._get_cinder_backend(summary, **kwargs)
            )
        )

    def _get_release(
        self,
        summary: VariantDeployment,
        **kwargs: Any
    ) -> Optional[str]:
        arguments = self.tools.argument_review

        if not arguments.is_release_requested(**kwargs):
            return None

        return summary.get_release()

    def _get_infra_type(
        self,
        summary: VariantDeployment,
        **kwargs: Any
    ) -> Optional[str]:
        arguments = self.tools.argument_review

        if not arguments.is_infra_type_requested(**kwargs):
            return None

        return summary.get_infra_type()

    def _get_nodes(
        self,
        summary: VariantDeployment,
        **kwargs: Any
    ) -> Optional[Dict[str, Node]]:
        arguments = self.tools.argument_review

        if not arguments.is_nodes_requested(**kwargs):
            return None

        nodes = summary.get_nodes()

        if not nodes:
            return None

        result = {}

        for node in nodes:
            result[node.name.value] = node

        return result

    def _get_topology(
        self,
        summary: VariantDeployment,
        **kwargs: Any
    ) -> Optional[str]:
        arguments = self.tools.argument_review

        if not arguments.is_topology_requested(**kwargs):
            return None

        return summary.get_topology()

    def _get_ip_version(
        self,
        summary: VariantDeployment,
        **kwargs: Any
    ) -> Optional[str]:
        arguments = self.tools.argument_review

        if not arguments.is_ip_version_requested(**kwargs):
            return None

        return summary.get_ip_version()

    def _get_neutron_backend(
        self,
        summary: VariantDeployment,
        **kwargs: Any
    ) -> Optional[str]:
        arguments = self.tools.argument_review

        if not arguments.is_network_backend_requested(**kwargs):
            return None

        return summary.get_neutron_backend()

    def _get_tls_everywhere(
        self,
        summary: VariantDeployment,
        **kwargs: Any
    ) -> Optional[str]:
        arguments = self.tools.argument_review

        if not arguments.is_tls_everywhere_requested(**kwargs):
            return None

        return summary.get_tls_everywhere()

    def _get_ml2_driver(
        self,
        summary: VariantDeployment,
        **kwargs: Any
    ) -> Optional[str]:
        arguments = self.tools.argument_review

        if not arguments.is_ml2_driver_requested(**kwargs):
            return None

        return summary.get_ml2_driver()

    def _get_cinder_backend(
        self,
        summary: VariantDeployment,
        **kwargs: Any
    ) -> Optional[str]:
        arguments = self.tools.argument_review

        if not arguments.is_cinder_backend_requested(**kwargs):
            return None

        return summary.get_cinder_backend()
