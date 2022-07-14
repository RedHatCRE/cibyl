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
from typing import Optional

from cached_property import cached_property
from dataclasses import dataclass

from cibyl.plugins.openstack.sources.zuul.deployments.outlines import \
    OutlineCreator
from cibyl.plugins.openstack.sources.zuul.variants import ReleaseSearch
from cibyl.sources.zuul.transactions import VariantResponse as Variant
from tripleo.insights import DeploymentLookUp, DeploymentSummary


class VariantDeployment:
    @dataclass
    class Tools:
        outline_creator = OutlineCreator()
        """Tests care of creating the TripleO outline for a Zuul job."""
        deployment_lookup = DeploymentLookUp()
        """Gets additional information on the deployment from TripleO."""
        release_search = ReleaseSearch()
        """Takes care of finding the release of the deployment."""

    def __init__(self, variant: Variant, tools: Tools = Tools()):
        self._variant = variant
        self._tools = tools

    @property
    def variant(self):
        return self._variant

    @property
    def tools(self):
        return self._tools

    @cached_property
    def _summary(self) -> DeploymentSummary:
        return self.tools.deployment_lookup.run(
            self.tools.outline_creator.new_outline_for(
                self.variant
            )
        )

    def get_release(self) -> Optional[str]:
        release = self.tools.release_search.search(self.variant)

        if not release:
            # No release defined -> Fall back to the default one
            return 'master'

        # Release defined -> Return its name
        _, value = release

        return value

    def get_infra_type(self) -> Optional[str]:
        return self._summary.infra_type

    def get_topology(self) -> Optional[str]:
        return str(self._summary.topology)

    def get_cinder_backend(self) -> Optional[str]:
        return self._summary.cinder_backend

    def get_ip_version(self) -> Optional[str]:
        return self._summary.ip_version


class VariantDeploymentFactory:
    def create_for(self, variant: Variant) -> VariantDeployment:
        return VariantDeployment(variant)
