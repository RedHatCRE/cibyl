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
from typing import Iterable, NamedTuple

from overrides import overrides

from cibyl.sources.zuul.apis.http import ZuulHTTPBuildAPI as Build
from cibyl.sources.zuul.utils.artifacts.manifest import (ManifestDir,
                                                         ManifestDownloader,
                                                         ManifestFileSearch)
from cibyl.sources.zuul.utils.tests.finder import TestFinder
from cibyl.sources.zuul.utils.tests.tempest.parser import TempestTestParser
from cibyl.sources.zuul.utils.tests.types import TestSuite

LOG = logging.getLogger(__name__)

SearchTerms = ManifestFileSearch.SearchTerms
"""Alias to reduce the type length."""


class TempestTestFinder(TestFinder):
    """Takes care of retrieving the results for all tempest tests executed
    by a build.
    """

    class Config(NamedTuple):
        """Defines the behaviour of this class.
        """
        DEFAULT_TEMPEST_SEARCH_TERMS = ManifestFileSearch.SearchTerms(
            paths=(ManifestDir('/logs/undercloud/var/log/tempest'),),
            files=('tempest_results.xml', 'tempest_results.xml.gz')
        )
        """Default files the class will look for to retrieve the test
        results."""

        search_terms: SearchTerms = DEFAULT_TEMPEST_SEARCH_TERMS
        """Location and name of all possible files that contain the test
        results."""

    class Tools(NamedTuple):
        """Tools this uses to perform its task.
        """
        manifest: ManifestDownloader = ManifestDownloader()
        """Allows to retrieve the manifest from a Zuul build."""
        search: ManifestFileSearch = ManifestFileSearch()
        """Allows to look for certain file within the manifest."""
        parser: TempestTestParser = TempestTestParser()
        """Allows to go from a xml string to python objects."""

    def __init__(self, config: Config = Config(), tools: Tools = Tools()):
        """Constructor.

        :param config: Configuration of this instance.
        :param tools: Tools this will use to do its task.
        """
        self._config = config
        self._tools = tools

    @property
    def config(self):
        """
        :return: Configuration of this instance.
        """
        return self._config

    @property
    def tools(self):
        """
        :return: Tools this will use to do its task.
        """
        return self._tools

    @overrides
    def find(self, build: Build) -> Iterable[TestSuite]:
        manifest = self.tools.manifest.download_from(build)
        result = self.tools.search.find_in(manifest, self.config.search_terms)

        if not result:
            LOG.warning(
                "Unable to find tempest results xml for build: '%s'",
                build.uuid
            )

            # Continue without any tests
            return ()

        file, _ = result

        return self.tools.parser.parse_tests_at(build, file)
