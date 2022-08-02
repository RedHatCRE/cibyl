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

from cibyl.sources.zuul.apis.rest import ZuulBuildRESTClient as Build
from cibyl.sources.zuul.utils.artifacts.manifest import ManifestFile
from cibyl.sources.zuul.utils.builds import get_url_to_log_file
from cibyl.sources.zuul.utils.tests.tempest.types import TempestTestSuite
from cibyl.utils.net import download_into_memory


class TempestTestParser:
    def __init__(self, build: Build):
        self._build = build

    @property
    def build(self):
        return self._build

    @property
    def session(self):
        return self.build.session.session

    def parser_tests_at(self, log: ManifestFile) -> Iterable[TempestTestSuite]:
        contents = self._download_build_file(log)
        return []

    def _download_build_file(self, file: ManifestFile) -> str:
        return download_into_memory(
            get_url_to_log_file(self.build, file),
            self.session
        )
