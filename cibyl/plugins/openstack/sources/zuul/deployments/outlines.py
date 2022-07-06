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
from cibyl.plugins.openstack.sources.zuul.variants import FeatureSetSearch
from cibyl.sources.zuul.transactions import VariantResponse
from tripleo.insights import DeploymentOutline


class OutlineCreator:
    """Factory for generation of :class:`DeploymentOutline`.
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

    def new_outline_for(self, variant: VariantResponse) -> DeploymentOutline:
        """Creates the outline of a deployment from the data found a job
        variant.

        :param variant: The variant to fetch data from.
        :return: The outline to be passed to TripleO Insights for such variant.
        """
        result = DeploymentOutline()
        result.featureset = self._get_featureset(variant, result.featureset)

        return result

    def _get_featureset(self, variant: VariantResponse, default: str) -> str:
        def search_featureset():
            search = self._tools.featureset_search.search(variant)

            if not search:
                return None

            _, value = search

            return value

        featureset = search_featureset()

        if not featureset:
            return default

        return self._tools.quickstart_paths.create_featureset_path(
            self._tools.quickstart_files.create_featureset(featureset)
        )
