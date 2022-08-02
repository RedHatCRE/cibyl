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
from typing import Iterable, NamedTuple

from overrides import overrides

from cibyl.models.ci.zuul.test_suite import TestSuite
from cibyl.sources.zuul.apis.rest import ZuulBuildRESTClient as Build
from cibyl.sources.zuul.utils.artifacts.manifest import (ManifestDir,
                                                         ManifestDownloader,
                                                         ManifestFileSearch)
from cibyl.sources.zuul.utils.tests.finder import TestFinder
from cibyl.sources.zuul.utils.tests.tempest.types import TempestTest

SearchTerms = ManifestFileSearch.SearchTerms


class TempestTestFinder(TestFinder):
    class Config(NamedTuple):
        DEFAULT_TEMPEST_SEARCH_TERMS = ManifestFileSearch.SearchTerms(
            paths=(ManifestDir('/logs/undercloud/var/log/tempest'),),
            files=('tempest_results.xml', 'tempest_results.xml.gz')
        )

        search_terms: SearchTerms = DEFAULT_TEMPEST_SEARCH_TERMS

    class Tools(NamedTuple):
        manifest: ManifestDownloader = ManifestDownloader()
        search: ManifestFileSearch = ManifestFileSearch()

    def __init__(self, config: Config = Config(), tools: Tools = Tools()):
        self._config = config
        self._tools = tools

    @property
    def config(self):
        return self._config

    @property
    def tools(self):
        return self._tools

    @overrides
    def find(self, build: Build) -> Iterable[TestSuite[TempestTest]]:
        manifest = self.tools.manifest.download_from(build)
        file = self.tools.search.find_in(manifest, self.config.search_terms)

        if not file:
            # TODO: Log a warning
            return ()

        result = []

        return result
