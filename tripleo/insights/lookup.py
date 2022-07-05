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
from typing import Iterable

import yaml

from tripleo.insights.deployment import FeatureSetInterpreter
from tripleo.insights.exceptions import InvalidURL
from tripleo.insights.git import GitDownloader, GitDownloaderFetcher
from tripleo.insights.io import DeploymentOutline, DeploymentSummary
from tripleo.insights.validation import OutlineValidator
from tripleo.utils.types import URL, YAML


class DeploymentLookUp:
    """Main class of the 'insights' library.

    Takes care of fetching all the required data in order to generate a
    deployment summary out of its outline.
    """

    def __init__(
        self,
        validator: OutlineValidator = OutlineValidator(),
        downloader_fetcher: GitDownloaderFetcher = GitDownloaderFetcher()
    ):
        """Constructor.

        :param validator: Tool used to validate the input data.
        :param downloader_fetcher: Tool used to get APIs to interact with Git.
        """
        self._validator = validator
        self._download_fetcher = downloader_fetcher

    @property
    def validator(self) -> OutlineValidator:
        """
        :return: Tool used to validate the input data.
        """
        return self._validator

    @property
    def download_fetcher(self) -> GitDownloaderFetcher:
        """
        :return: Tool used to get APIs to interact with Git.
        """
        return self._download_fetcher

    def run(self, outline: DeploymentOutline) -> DeploymentSummary:
        """Runs a lookup task, fetching all the necessary data out of the
        TripleO repositories in order to understand what deployment would be
        performed from it.

        :param outline: Points to the files that describe the deployment
            TripleO will perform.
        :return: A summary of such deployment where TripleO to do it.
        """
        result = DeploymentSummary()

        self._validate_outline(outline)

        for api in self._get_apis_for(outline.quickstart):
            featureset = FeatureSetInterpreter(
                data=self._download_yaml(api, file=outline.featureset),
                overrides=outline.overrides
            )

            result.ip_version = 'IPv6' if featureset.is_ipv6() else 'IPv4'

        return result

    def _validate_outline(self, outline: DeploymentOutline) -> None:
        is_valid, error = self.validator.validate(outline)

        if not is_valid:
            raise error

    def _get_apis_for(self, url: URL) -> Iterable[GitDownloader]:
        result = self._download_fetcher.get_downloaders_for(url)

        if not result:
            raise InvalidURL(f"Found no handlers for URL: '{url}'.")

        return result

    def _download_yaml(self, api: GitDownloader, file: str) -> YAML:
        return yaml.safe_load(api.download_as_text(file))
