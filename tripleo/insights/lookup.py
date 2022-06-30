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
    def __init__(
        self,
        validator: OutlineValidator = OutlineValidator(),
        downloader_fetcher: GitDownloaderFetcher = GitDownloaderFetcher()
    ):
        self._validator = validator
        self._download_fetcher = downloader_fetcher

    @property
    def validator(self) -> OutlineValidator:
        return self._validator

    @property
    def download_fetcher(self) -> GitDownloaderFetcher:
        return self._download_fetcher

    def run(self, outline: DeploymentOutline) -> DeploymentSummary:
        result = DeploymentSummary()

        self._validate_outline(outline)

        for api in self._get_apis_for(outline.quickstart):
            featureset = FeatureSetInterpreter(
                self._download_yaml(api, file=outline.featureset)
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
