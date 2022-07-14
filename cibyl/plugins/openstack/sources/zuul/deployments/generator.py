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
from typing import Any

from cibyl.plugins.openstack import Deployment
from cibyl.plugins.openstack.network import Network
from cibyl.plugins.openstack.sources.zuul.deployments.outlines import \
    OutlineCreator
from cibyl.plugins.openstack.sources.zuul.variants import ReleaseSearch
from cibyl.plugins.openstack.storage import Storage
from cibyl.sources.zuul.transactions import VariantResponse as Variant
from tripleo.insights import DeploymentLookUp


class DeploymentGenerator:
    """Factory for generation of :class:`Deployment`.
    """

    class Tools:
        """Tools the factory will use to do its task.
        """
        outline_creator = OutlineCreator()
        """Tests care of creating the TripleO outline for a Zuul job."""
        deployment_lookup = DeploymentLookUp()
        """Gets additional information on the deployment from TripleO."""
        release_search = ReleaseSearch()
        """Takes care of finding the release of the deployment."""

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
        summary = self.tools.deployment_lookup.run(
            self.tools.outline_creator.new_outline_for(variant)
        )

        return Deployment(
            release=self._get_release(variant, **kwargs),
            infra_type=summary.infra_type,
            topology=str(summary.topology),
            storage=Storage(
                cinder_backend=summary.cinder_backend
            ),
            network=Network(
                ip_version=summary.ip_version
            )
        )

    def _get_release(self, variant: Variant, **kwargs: Any) -> str:
        release_search = self.tools.release_search

        if any(term in kwargs for term in ('spec', 'release')):
            release = release_search.search(variant)

            if not release:
                # Fall back to the default value
                return 'master'

            _, value = release

            return value

        # Nothing means to not output this field.
        return ''
