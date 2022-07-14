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
from typing import Any, Optional

from cibyl.plugins.openstack import Deployment
from cibyl.plugins.openstack.network import Network
from cibyl.plugins.openstack.sources.zuul.deployments.arguments import \
    ArgumentReview
from cibyl.plugins.openstack.sources.zuul.deployments.summary import (
    VariantDeployment, VariantDeploymentFactory)
from cibyl.plugins.openstack.storage import Storage
from cibyl.sources.zuul.transactions import VariantResponse as Variant


class DeploymentGenerator:
    """Factory for generation of :class:`Deployment`.
    """

    class Tools:
        """Tools the factory will use to do its task.
        """
        argument_review = ArgumentReview()
        variant_summary = VariantDeploymentFactory()

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
            topology=self._get_topology(summary, **kwargs),
            storage=Storage(
                cinder_backend=self._get_cinder_backend(summary, **kwargs)
            ),
            network=Network(
                ip_version=self._get_ip_version(summary, **kwargs)
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

    def _get_topology(
        self,
        summary: VariantDeployment,
        **kwargs: Any
    ) -> Optional[str]:
        arguments = self.tools.argument_review

        if not arguments.is_topology_requested(**kwargs):
            return None

        return summary.get_topology()

    def _get_cinder_backend(
        self,
        summary: VariantDeployment,
        **kwargs: Any
    ) -> Optional[str]:
        arguments = self.tools.argument_review

        if not arguments.is_cinder_backend_requested(**kwargs):
            return None

        return summary.get_cinder_backend()

    def _get_ip_version(
        self,
        summary: VariantDeployment,
        **kwargs: Any
    ) -> Optional[str]:
        arguments = self.tools.argument_review

        if not arguments.is_ip_version_requested(**kwargs):
            return None

        return summary.get_cinder_backend()
