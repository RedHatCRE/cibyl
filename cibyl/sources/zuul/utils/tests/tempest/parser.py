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
from typing import Iterable, NamedTuple, List, Optional

from dataclasses import dataclass, field
from requests import Session
from xsdata.formats.dataclass.parsers import XmlParser

from cibyl.models.ci.zuul.test_suite import TestSuite
from cibyl.sources.zuul.apis.rest import ZuulBuildRESTClient as Build
from cibyl.sources.zuul.utils.artifacts.manifest import ManifestFile
from cibyl.sources.zuul.utils.builds import get_url_to_log_file
from cibyl.utils.net import download_into_memory


@dataclass
class ZuulTempestSkipped:
    value: str = field()


@dataclass
class ZuulTempestFailure:
    type: str = field(
        metadata={
            'type': 'Attribute'
        }
    )
    value: str = field()


@dataclass
class ZuulTempestTestCase:
    name: str = field(
        metadata={
            'type': 'Attribute'
        }
    )
    classname: str = field(
        metadata={
            'type': 'Attribute'
        }
    )
    time: float = field(
        metadata={
            'type': 'Attribute'
        }
    )
    failure: Optional[ZuulTempestFailure] = field(
        default=None,
        metadata={
            'type': 'Element'
        }
    )
    skipped: Optional[ZuulTempestSkipped] = field(
        default=None,
        metadata={
            'type': 'Element'
        }
    )


@dataclass
class ZuulTempestTestSuite:
    errors: int = field(
        metadata={
            'type': 'Attribute'
        }
    )
    failures: int = field(
        metadata={
            'type': 'Attribute'
        }
    )
    name: str = field(
        metadata={
            'type': 'Attribute'
        }
    )
    tests: int = field(
        metadata={
            'type': 'Attribute'
        }
    )
    time: float = field(
        metadata={
            'type': 'Attribute'
        }
    )
    testcase: List[ZuulTempestTestCase] = field(
        default_factory=list,
        metadata={
            'type': 'Element'
        }
    )


class TempestTestParser:
    class Tools(NamedTuple):
        parser: XmlParser = XmlParser()

    def __init__(self, tools: Tools = Tools()):
        self._tools = tools

    @property
    def tools(self):
        return self._tools

    def parser_tests_at(
        self,
        build: Build,
        log: ManifestFile
    ) -> Iterable[TestSuite]:
        suite = self.tools.parser.from_string(
            self._download_build_file(build, log),
            ZuulTempestTestSuite
        )

        return []

    def _download_build_file(self, build: Build, file: ManifestFile) -> str:
        return download_into_memory(
            get_url_to_log_file(build, file),
            self._get_session_from(build)
        )

    def _get_session_from(self, build: Build) -> Session:
        return build.session.session
