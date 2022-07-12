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

from tripleo.insights.deployment import (EnvironmentInterpreter,
                                         FeatureSetInterpreter,
                                         NodesInterpreter, ReleaseInterpreter,
                                         ScenarioInterpreter)
from tripleo.insights.git import GitDownload
from tripleo.insights.io import DeploymentOutline, DeploymentSummary
from tripleo.insights.tripleo import THTBranchCreator, THTPathCreator
from tripleo.insights.validation import OutlineValidator

LOG = logging.getLogger(__name__)


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

        downloader = GitDownload()
        """Used to download the scenario file."""

    def __init__(self, tools: Tools = Tools()):
        """Constructor.

        :param tools: Tools used by the class to perform its task.
        """
        self._tools = tools

    @property
    def tools(self):
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
            self.tools.downloader.download_as_yaml(
                repo=outline.heat,
                branch=branch_creator.create_release_branch(release),
                file=path_creator.create_scenario_path(scenario)
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

        scenario_factory: ScenarioFactory = ScenarioFactory()
        """Used to created the scenario interpreter."""

    def __init__(self, tools: Tools = Tools()):
        """Constructor.

        :param tools: The tools this will use to do its task.
        """
        self._tools = tools

    @property
    def tools(self):
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
            self.tools.downloader.download_as_yaml(
                repo=outline.quickstart,
                file=outline.environment
            ),
            overrides=outline.overrides
        )

        featureset = FeatureSetInterpreter(
            self.tools.downloader.download_as_yaml(
                repo=outline.quickstart,
                file=outline.featureset
            ),
            overrides=outline.overrides
        )

        nodes = NodesInterpreter(
            self.tools.downloader.download_as_yaml(
                repo=outline.quickstart,
                file=outline.nodes
            ),
            overrides=outline.overrides
        )

        release = ReleaseInterpreter(
            self.tools.downloader.download_as_yaml(
                repo=outline.quickstart,
                file=outline.release
            ),
            overrides=outline.overrides
        )

        scenario = self.tools.scenario_factory.from_interpreters(
            outline, featureset, release
        )

        result = DeploymentSummary()

        result.infra_type = environment.get_intra_type()
        result.ip_version = '6' if featureset.is_ipv6() else '4'
        result.topology = nodes.get_topology()
        result.release = release.get_release_name()
        result.cinder_backend = scenario.get_cinder_backend()

        return result
