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
from dataclasses import dataclass, field
from typing import Iterable, List, NamedTuple, Optional

from requests import Session
from xsdata.formats.dataclass.parsers import XmlParser

from cibyl.sources.zuul.apis.rest import ZuulBuildRESTClient as Build
from cibyl.sources.zuul.utils.artifacts.manifest import ManifestFile
from cibyl.sources.zuul.utils.builds import get_url_to_build_file
from cibyl.sources.zuul.utils.tests.tempest.types import TempestTest
from cibyl.sources.zuul.utils.tests.types import TestResult, TestSuite
from cibyl.utils.net import download_into_memory
from tripleo.utils.urls import URL


@dataclass
class XMLTempestSkipped:
    value: str = field()


@dataclass
class XMLTempestFailure:
    type: str = field(
        metadata={
            'type': 'Attribute'
        }
    )
    value: str = field()


@dataclass
class XMLTempestTestCase:
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
    failure: Optional[XMLTempestFailure] = field(
        default=None,
        metadata={
            'type': 'Element'
        }
    )
    skipped: Optional[XMLTempestSkipped] = field(
        default=None,
        metadata={
            'type': 'Element'
        }
    )


@dataclass
class XMLTempestTestSuite:
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
    testcase: List[XMLTempestTestCase] = field(
        default_factory=list,
        metadata={
            'type': 'Element'
        }
    )


class XMLToTest:
    def to_test(self, url: URL, case: XMLTempestTestCase) -> TempestTest:
        return TempestTest(
            name=case.name,
            result=self._get_case_result(case),
            duration=case.time,
            url=url,
            class_name=case.classname,
            skip_reason=case.skipped.value if case.skipped else None,
            failure_reason=case.failure.value if case.failure else None
        )

    def _get_case_result(self, case: XMLTempestTestCase) -> TestResult:
        if case.skipped:
            return TestResult.SKIPPED

        if case.failure:
            return TestResult.FAILURE

        return TestResult.SUCCESS


class XMLToTestSuite:
    class Tools(NamedTuple):
        cases: XMLToTest = XMLToTest()

    def __init__(self, tools: Tools = Tools()):
        self._tools = tools

    @property
    def tools(self):
        return self._tools

    def to_suite(self, url: URL, suite: XMLTempestTestSuite) -> TestSuite:
        return TestSuite(
            name=suite.name,
            url=url,
            tests=[
                self.tools.cases.to_test(url, case)
                for case in suite.testcase
            ]
        )


class TempestTestParser:
    class Tools(NamedTuple):
        parser: XmlParser = XmlParser()
        converter: XMLToTestSuite = XMLToTestSuite()

    def __init__(self, tools: Tools = Tools()):
        self._tools = tools

    @property
    def tools(self):
        return self._tools

    def parse_tests_at(
        self,
        build: Build,
        file: ManifestFile
    ) -> Iterable[TestSuite]:
        return [
            self.tools.converter.to_suite(
                url=self._get_url_to_file(build, file),
                suite=self.tools.parser.from_string(
                    self._download_build_file(build, file),
                    XMLTempestTestSuite
                )
            )
        ]

    def _download_build_file(self, build: Build, file: ManifestFile) -> str:
        return download_into_memory(
            self._get_url_to_file(build, file),
            self._get_session_from(build)
        )

    def _get_url_to_file(self, build: Build, file: ManifestFile) -> URL:
        return get_url_to_build_file(build, file)

    def _get_session_from(self, build: Build) -> Session:
        return build.session.session
