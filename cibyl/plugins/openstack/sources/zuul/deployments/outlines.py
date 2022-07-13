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
from typing import Any, Tuple

from cibyl.plugins.openstack.sources.zuul.tripleo import (
    QuickStartFileCreator, QuickStartPathCreator)
from cibyl.plugins.openstack.sources.zuul.variants import (FeatureSetSearch,
                                                           InfraTypeSearch,
                                                           NodesSearch,
                                                           ReleaseNameSearch)
from cibyl.sources.zuul.transactions import VariantResponse as Variant
from tripleo.insights import DeploymentOutline


class OverridesCollector:
    """Tools used to gather all the overrides the job defines over the
    TripleO deployment.
    """

    @dataclass
    class Defaults:
        """Defines the overrides to fall back to in case none are available.
        """
        infra_type: Tuple[str, str] = ('environment_type', 'standalone')

    @dataclass
    class Tools:
        """Tools the factory will use to do its task.
        """
        infra_type_search = InfraTypeSearch()
        """Checks whether there is an override for 'infra_type'."""

    def __init__(
        self,
        defaults: Defaults = Defaults(),
        tools: Tools = Tools()
    ):
        """Constructor.

        :param defaults: Default overrides to use in case custom ones
            cannot be found. The values defined here will always be part of
            the output of this class, had the target element had an override
            for the item or not.
        :param tools: The tools this will use.
        """
        self._defaults = defaults
        self._tools = tools

    @property
    def defaults(self) -> Defaults:
        """
        :return: Default overrides to use in case custom ones cannot be found.
        """
        return self._defaults

    @property
    def tools(self) -> Tools:
        """
        :return: The tools this will use.
        """
        return self._tools

    def collect_overrides_for(self, variant: Variant) -> dict:
        """Collects all the known overrides that a variant may apply on top
        of the TripleO deployment.

        :param variant: The variant to fetch data from.
        :return: A dictionary that matches a deployment item to its
            overridden value.
        """
        result = self._default_overrides()

        self._handle_infra_type(variant, result)

        return result

    def _default_overrides(self) -> dict:
        """
        :return: Dictionary with all default overrides preinstalled.
        """
        result = {}

        self._insert_tuple(result, self.defaults.infra_type)

        return result

    def _handle_infra_type(self, variant: Variant, overrides: dict) -> None:
        """Updates 'overrides' with any custom 'infra_type' override the
        variant may have. Leaves 'overrides' as is if there is none.

        :param variant: The variant to fetch data from.
        :param overrides: The dictionary containing the overrides.
        """
        infra_type = self.tools.infra_type_search.search(variant)

        if not infra_type:
            return

        self._insert_tuple(overrides, infra_type)

    def _insert_tuple(self, target: dict, entry: Tuple[Any, Any]) -> None:
        """Inserts a two-element tuple into a dictionary interpreting it as
        (key, value). If the key already exists in the dictionary, then its
        value is overridden.

        :param target: The dictionary to modify.
        :param entry: The tuple to insert.
        """
        key, val = entry
        target[key] = val


class FilesFetcher:
    """Tool used to find the files that describe a deployment.
    """

    @dataclass
    class Tools:
        """Tools this will use to do its task.
        """
        quickstart_files = QuickStartFileCreator()
        """Factory for creating the name of files at the QuickStart repo."""
        quickstart_paths = QuickStartPathCreator()
        """Factory for creating paths relative to the QuickStart repo root."""
        featureset_search = FeatureSetSearch()
        """Takes care of finding the featureset of the outline."""
        nodes_search = NodesSearch()
        """Takes care of finding the nodes of the outline."""
        release_search = ReleaseNameSearch()
        """Takes care of finding the release of the outline."""

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

    def fetch_featureset(self, variant: Variant, default: str) -> str:
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

    def fetch_nodes(self, variant: Variant, default: str) -> str:
        """Studies a variant in order to determine the nodes file on
        TripleO QuickStart that its deployment uses.

        :param variant: The variant to fetch data from.
        :param default: Path to the default nodes file that will be
            returned in case the variant has no custom one.
        :return: Path to the nodes file of the variant.
        """
        nodes = self.tools.nodes_search.search(variant)

        if not nodes:
            return default

        _, value = nodes

        return self.tools.quickstart_paths.create_nodes_path(
            self.tools.quickstart_files.create_nodes(value)
        )

    def fetch_release(self, variant: Variant, default: str) -> str:
        """Studies a variant in order to determine the release file on
        TripleO QuickStart that its deployment uses.

        :param variant: The variant to fetch data from.
        :param default: Path to the default release file that will be
            returned in case the variant has no custom one.
        :return: Path to the release file of the variant.
        """
        release = self.tools.release_search.search(variant)

        if not release:
            return default

        _, value = release

        return self.tools.quickstart_paths.create_release_path(
            self.tools.quickstart_files.create_release(value)
        )


class OutlineCreator:
    """Factory for generation of :class:`DeploymentOutline`.
    """

    @dataclass
    class Tools:
        """Tools the factory will use to do its task.
        """
        files_fetcher = FilesFetcher()
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

    def new_outline_for(self, variant: Variant) -> DeploymentOutline:
        """Creates the outline of a deployment from the data found a job
        variant.

        :param variant: The variant to fetch data from.
        :return: The outline to be passed to TripleO Insights for such variant.
        """
        result = DeploymentOutline()

        result.featureset = self._get_featureset(variant, result.featureset)
        result.nodes = self._get_nodes(variant, result.nodes)
        result.release = self._get_release(variant, result.release)
        result.overrides = self._get_overrides(variant)

        return result

    def _get_featureset(self, variant: Variant, default: str) -> str:
        return self.tools.files_fetcher.fetch_featureset(variant, default)

    def _get_nodes(self, variant: Variant, default: str) -> str:
        return self.tools.files_fetcher.fetch_nodes(variant, default)

    def _get_release(self, variant: Variant, default: str) -> str:
        return self.tools.files_fetcher.fetch_release(variant, default)

    def _get_overrides(self, variant: Variant) -> dict:
        return self.tools.overrides_collector.collect_overrides_for(variant)
