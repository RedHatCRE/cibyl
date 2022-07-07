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

from cibyl.plugins.openstack.sources.zuul.tripleo import (
    QuickStartFileCreator, QuickStartPathCreator)
from cibyl.plugins.openstack.sources.zuul.variants import (FeatureSetSearch,
                                                           InfraTypeSearch)
from cibyl.sources.zuul.transactions import VariantResponse
from tripleo.insights import DeploymentOutline


class OverridesCollector:
    """Tools used to gather all the overrides the job defines over the
    TripleO deployment.
    """

    @dataclass
    class Tools:
        """Tools the factory will use to do its task.
        """
        infra_type_search = InfraTypeSearch()
        """Checks whether there is an override for 'infra_type'."""

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

    def collect_overrides_for(self, variant: VariantResponse) -> dict:
        """Collects all the known overrides that a variant may apply on top
        of the TripleO deployment.

        :param variant: The variant to fetch data from.
        :return: A dictionary that matches a deployment item to its
            overridden value.
        """
        result = {}

        self._handle_infra_type(variant, result)

        return result

    def _handle_infra_type(
        self,
        variant: VariantResponse,
        overrides: dict,
    ) -> None:
        infra_type = self.tools.infra_type_search.search(variant)

        if infra_type:
            variable, value = infra_type
            overrides[variable] = value


class FeatureSetFetcher:
    """Tool used to find any custom featureset a job may define.
    """

    @dataclass
    class Tools:
        """Tools the factory will use to do its task.
        """
        quickstart_files = QuickStartFileCreator()
        """Factory for creating the name of files at the QuickStart repo."""
        quickstart_paths = QuickStartPathCreator()
        """Factory for creating paths relative to the QuickStart repo root."""
        featureset_search = FeatureSetSearch()
        """Takes care of finding the featureset of the outline."""

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

    def fetch_featureset(self, variant: VariantResponse, default: str) -> str:
        """Studies a variant in order to determine the featureset file on
        TripleO QuickStart that its deployment uses.

        :param variant: The variant to fetch data from.
        :param default: Path to the default featureset file that will be
            returned in case the variant has no custom one.
        :return: Path to the featureset file of the variant.
        """
        featureset = self.tools.featureset_search.search(variant)

        if not featureset:
            return default

        _, value = featureset

        return self.tools.quickstart_paths.create_featureset_path(
            self.tools.quickstart_files.create_featureset(value)
        )


class OutlineCreator:
    """Factory for generation of :class:`DeploymentOutline`.
    """

    @dataclass
    class Tools:
        """Tools the factory will use to do its task.
        """
        featureset_fetcher = FeatureSetFetcher()
        overrides_collector = OverridesCollector()

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

    def new_outline_for(self, variant: VariantResponse) -> DeploymentOutline:
        """Creates the outline of a deployment from the data found a job
        variant.

        :param variant: The variant to fetch data from.
        :return: The outline to be passed to TripleO Insights for such variant.
        """
        result = DeploymentOutline()
        result.featureset = self._get_featureset(variant, result.featureset)
        result.overrides = self._get_overrides(variant)

        return result

    def _get_featureset(self, variant: VariantResponse, default: str) -> str:
        return self.tools.featureset_fetcher.fetch_featureset(variant, default)

    def _get_overrides(self, variant: VariantResponse) -> dict:
        return self.tools.overrides_collector.collect_overrides_for(variant)
