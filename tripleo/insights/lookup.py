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
import logging
from dataclasses import dataclass
from typing import NamedTuple, Optional

from tripleo.insights.git import GitDownload
from tripleo.insights.interpreters import (EnvironmentInterpreter,
                                           FeatureSetInterpreter,
                                           NodesInterpreter,
                                           ReleaseInterpreter,
                                           ScenarioInterpreter)
from tripleo.insights.io import DeploymentOutline, DeploymentSummary
from tripleo.insights.tripleo import THTBranchCreator, THTPathCreator
from tripleo.insights.validation import OutlineValidator
from tripleo.utils.cache import Cache
from tripleo.utils.urls import URL
from tripleo.utils.yaml import YAML

LOG = logging.getLogger(__name__)


class Resource(NamedTuple):
    """Defines a resource that contributes to outlining the deployment.
    """
    repo: URL
    """Repository where the resource is at."""
    file: str
    """Relative path to the repository's root pointing to the resource file."""
    branch: Optional[str] = None
    """Branch where the file is at. 'None' for default branch of repository."""


class ScenarioFactory:
    """Used to build scenario interpreters from more heterogeneous inputs.
    """

    @dataclass
    class Tools:
        """Collection of tools used by the class to perform its task.
        """
        branch_creator = THTBranchCreator()
        """Used to generate the branch name for a certain release."""
        path_creator = THTPathCreator()
        """Used to generate path to the scenario file."""

    def __init__(
        self,
        cache: Cache[Resource, YAML],
        tools: Tools = Tools()
    ):
        """Constructor.

        :param cache: Storage for resources this reads from.
        :param tools: Tools used by the class to perform its task.
        """
        self._cache = cache
        self._tools = tools

    @property
    def cache(self) -> Cache[Resource, YAML]:
        """
        :return: Storage where resources this depends on are saved at.
        """
        return self._cache

    @property
    def tools(self) -> Tools:
        """
        :return: Tools used by the class to perform its task.
        """
        return self._tools

    def from_interpreters(
        self,
        outline: DeploymentOutline,
        featureset: FeatureSetInterpreter,
        release: ReleaseInterpreter
    ) -> ScenarioInterpreter:
        """Builds a new interpreter out of the data extracted from others.

        :param outline: Outline shared by the interpreters.
        :param featureset: Gets data from the featureset file.
        :param release: Gets data from the release file.
        :return: An interpreter for the scenario indicated by the featureset.
        :raises ValueError: If the featureset points to no scenario file.
        """
        branch_creator = self.tools.branch_creator
        path_creator = self.tools.path_creator

        release = release.get_release_name()
        scenario = featureset.get_scenario()

        if not scenario:
            raise ValueError(
                'Featureset has no scenario. '
                'One is required for the interpreter to be build.'
            )

        return ScenarioInterpreter(
            self.cache.get(
                Resource(
                    repo=outline.heat,
                    file=path_creator.create_scenario_path(scenario),
                    branch=branch_creator.create_release_branch(release)
                )
            ),
            overrides=outline.overrides
        )


class DeploymentLookUp:
    """Main class of the 'insights' library.

    Takes care of fetching all the required data in order to generate a
    deployment summary out of its outline.
    """

    @dataclass
    class Tools:
        """Collection of tools used by the class to perform its task.
        """
        validator: OutlineValidator = OutlineValidator()
        """Tool used to validate the input data."""
        downloader: GitDownload = GitDownload()
        """Tool used to download files from Git repositories."""

    def __init__(
        self,
        cache: Optional[Cache[Resource, YAML]] = None,
        scenarios: Optional[ScenarioFactory] = None,
        tools: Tools = Tools()
    ):
        """Constructor.

        :param cache: Storage where resources this uses are contained in.
            'None' to allow this to create its own.
        :param scenarios: Utility used to create scenario interpreters from
            complex inputs. 'None' to allow this to create its own.
        :param tools: The tools this will use to do its task.
        """
        if cache is None:
            def loader(resource: Resource) -> YAML:
                return self.tools.downloader.download_as_yaml(
                    repo=resource.repo,
                    file=resource.file,
                    branch=resource.branch
                )

            cache = Cache[Resource, YAML](
                loader=loader,
                storage=None  # Let the cache set up its own container
            )

        if scenarios is None:
            scenarios = ScenarioFactory(
                cache=cache  # Reuse the same cache for all interpreters
            )

        self._cache = cache
        self._scenarios = scenarios
        self._tools = tools

    @property
    def cache(self) -> Cache[Resource, YAML]:
        """
        :return: Storage where resources this depends on are saved at.
        """
        return self._cache

    @property
    def scenarios(self) -> ScenarioFactory:
        """
        :return: Utility used to create scenario interpreters from complex
            inputs.
        """
        return self._scenarios

    @property
    def tools(self) -> Tools:
        """
        :return: The tools this will use to do its task.
        """
        return self._tools

    def run(self, outline: DeploymentOutline) -> DeploymentSummary:
        """Runs a lookup task, fetching all the necessary data out of the
        TripleO repositories in order to understand what deployment would be
        performed from it.

        :param outline: Points to the files that describe the deployment
            TripleO will perform.
        :return: A summary of such deployment where TripleO to do it.
        """
        self._validate_outline(outline)

        return self._generate_deployment(outline)

    def _validate_outline(self, outline: DeploymentOutline) -> None:
        is_valid, error = self.tools.validator.validate(outline)

        if not is_valid:
            raise error

    def _generate_deployment(
        self,
        outline: DeploymentOutline
    ) -> DeploymentSummary:
        environment = EnvironmentInterpreter(
            self.cache.get(
                Resource(
                    repo=outline.quickstart,
                    file=outline.environment
                )
            ),
            overrides=outline.overrides
        )

        featureset = FeatureSetInterpreter(
            self.cache.get(
                Resource(
                    repo=outline.quickstart,
                    file=outline.featureset
                )
            ),
            overrides=outline.overrides
        )

        nodes = NodesInterpreter(
            self.cache.get(
                Resource(
                    repo=outline.quickstart,
                    file=outline.nodes
                )
            ),
            overrides=outline.overrides
        )

        release = ReleaseInterpreter(
            self.cache.get(
                Resource(
                    repo=outline.quickstart,
                    file=outline.release
                )
            ),
            overrides=outline.overrides
        )

        result = DeploymentSummary()

        result.release = release.get_release_name()
        result.infra_type = environment.get_intra_type()
        result.topology = nodes.get_topology()

        # Giving default values
        result.components.neutron.ip_version = '4'
        result.components.neutron.tls_everywhere = 'Off'

        if featureset.is_ipv6():
            result.components.neutron.ip_version = '6'

        if featureset.is_tls_everywhere_enabled():
            result.components.neutron.tls_everywhere = 'On'

        # Take care of the scenario file too
        if featureset.get_scenario():
            scenario = self.scenarios.from_interpreters(
                outline, featureset, release
            )

            result.components.cinder.backend = scenario.get_cinder_backend()
            result.components.neutron.backend = scenario.get_neutron_backend()
            result.components.neutron.ml2_driver = scenario.get_ml2_driver()

        return result
