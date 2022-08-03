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

from cibyl.sources.zuul.apis.http import ZuulHTTPBuildAPI as Build
from cibyl.sources.zuul.utils.artifacts.manifest import ManifestFile
from cibyl.sources.zuul.utils.builds import get_url_to_build_file
from cibyl.sources.zuul.utils.tests.tempest.types import TempestTest
from cibyl.sources.zuul.utils.tests.types import TestResult, TestSuite
from cibyl.utils.net import download_into_memory
from tripleo.utils.urls import URL


@dataclass
class XMLTempestSkipped:
    """Field containing the reason why a test case got skipped.
    """
    value: str = field()
    """The reason itself."""


@dataclass
class XMLTempestFailure:
    """Field containing the reason why a test case failed.
    """
    type: str = field(
        metadata={
            'type': 'Attribute'
        }
    )
    """The type of error that made the test case fail."""
    value: str = field()
    """An explanation on why the error happened."""


@dataclass
class XMLTempestTestCase:
    """Representation of a test case as seen on the test results XML. Used
    to unmarshall such document.
    """
    name: str = field(
        metadata={
            'type': 'Attribute'
        }
    )
    """Name of the test."""
    classname: str = field(
        metadata={
            'type': 'Attribute'
        }
    )
    """Path to the object that holds this test case."""
    time: float = field(
        metadata={
            'type': 'Attribute'
        }
    )
    """Amount of seconds it took to complete."""
    failure: Optional[XMLTempestFailure] = field(
        default=None,
        metadata={
            'type': 'Element'
        }
    )
    """Reason why the test case failed. If 'None', it did not."""
    skipped: Optional[XMLTempestSkipped] = field(
        default=None,
        metadata={
            'type': 'Element'
        }
    )
    """Reason why the test case was skipped. If 'None', it was not."""


@dataclass
class XMLTempestTestSuite:
    """Representation of a test suite as seen on the test results XML. Used
    to unmarshall such document.
    """
    errors: int = field(
        metadata={
            'type': 'Attribute'
        }
    )
    """Number of test cases that resulted in an error."""
    failures: int = field(
        metadata={
            'type': 'Attribute'
        }
    )
    """Number of test cases that resulted in a failure."""
    name: str = field(
        metadata={
            'type': 'Attribute'
        }
    )
    """Name of the suite."""
    tests: int = field(
        metadata={
            'type': 'Attribute'
        }
    )
    """Number of tests that were executed."""
    time: float = field(
        metadata={
            'type': 'Attribute'
        }
    )
    """Amount of seconds the suite took to complete."""
    testcase: List[XMLTempestTestCase] = field(
        default_factory=list,
        metadata={
            'type': 'Element'
        }
    )
    """Collection will all the test cases that were run."""


class XMLToTest:
    """Converts an XML test case into a Cibyl test.
    """

    def to_test(self, url: URL, case: XMLTempestTestCase) -> TempestTest:
        """Converts the XML object into something that Cibyl can understand.

        :param url: URL where the test case was read from.
        :param case: The XML test case.
        :return: Cibyl representation of that test case.
        """
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
    """Converts an XML test suite into a Cibyl test suite.
    """

    class Tools(NamedTuple):
        """Tools this will use to do its task.
        """
        cases: XMLToTest = XMLToTest()
        """Used to convert test cases within the test suite."""

    def __init__(self, tools: Tools = Tools()):
        """Constructor.

        :param tools: Tools this will use to do its task.
        """
        self._tools = tools

    @property
    def tools(self):
        """
        :return: Tools this will use to do its task.
        """
        return self._tools

    def to_suite(self, url: URL, suite: XMLTempestTestSuite) -> TestSuite:
        """Converts the XML object into something that Cibyl can understand.

        :param url: URL where the test case was read from.
        :param suite: The XML test suite.
        :return: Cibyl representation of that test suite.
        """
        return TestSuite(
            name=suite.name,
            url=url,
            tests=[
                self.tools.cases.to_test(url, case)
                for case in suite.testcase
            ]
        )


class TempestTestParser:
    """Tools used to convert the XML test results file into a collection of
    objects that Cibyl can understand.
    """

    class Tools(NamedTuple):
        """Tools this will use to do its task.
        """
        parser: XmlParser = XmlParser()
        """Used to go from a XML string to Python representation of such
        file."""
        converter: XMLToTestSuite = XMLToTestSuite()
        """Used to go from the intermediate Python representation to
        something Cibyl may use."""

    def __init__(self, tools: Tools = Tools()):
        """Constructor.

        :param tools: Tools this will use to do its task.
        """
        self._tools = tools

    @property
    def tools(self):
        """
        :return: Tools this will use to do its task.
        """
        return self._tools

    def parse_tests_at(
        self,
        build: Build,
        file: ManifestFile
    ) -> Iterable[TestSuite]:
        """Downloads and parses the XML file that describes the result of
        all tempest test cases.

        :param build: The build that exported the file.
        :param file: Relative path pointing to the XML file that holds the
            test results.
        :return: The tests within the XML file, formatted for Cibyl to use.
        """
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
