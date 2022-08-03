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
from unittest import TestCase
from unittest.mock import Mock, call, patch

from cibyl.sources.zuul.utils.tests.tempest.parser import (TempestTestParser,
                                                           XMLTempestTestSuite,
                                                           XMLToTest,
                                                           XMLToTestSuite)
from cibyl.sources.zuul.utils.tests.types import TestResult


class TestXMLToTestSuite(TestCase):
    """Tests for :class:`XMLToTestSuite`.
    """

    def test_xml_to_suite(self):
        """Checks that the class is capable of transforming the xml data in
        to a cibyl test suite.
        """
        test = Mock()
        case = Mock()

        url = Mock()
        suite = Mock()
        suite.name = 'suite'
        suite.testcase = [case]

        cases = Mock()
        cases.to_test = Mock()
        cases.to_test.return_value = test

        tools = Mock()
        tools.cases = cases

        converter = XMLToTestSuite(tools=tools)

        result = converter.to_suite(url, suite)

        self.assertEqual(suite.name, result.name)
        self.assertEqual(url, result.url)
        self.assertEqual([test], result.tests)

        cases.to_test.assert_called_with(url, case)


class TestXMLToTest(TestCase):
    """Tests for :class:`XMLToTest`.
    """

    def test_unconditional_xml_to_test(self):
        """Checks the conversion done on those fields that do not have any
        conditions to them.
        """
        url = Mock()
        case = Mock()
        case.name = 'case'
        case.time = 1.0
        case.classname = 'classname'

        converter = XMLToTest()

        result = converter.to_test(url, case)

        self.assertEqual(case.name, result.name)
        self.assertEqual(case.time, result.duration)
        self.assertEqual(url, result.url)
        self.assertEqual(case.classname, result.class_name)

    def test_result(self):
        """Checks the result given to the test for multiple conditions.
        """
        case = Mock()

        converter = XMLToTest()

        case.skipped = None
        case.failure = None

        self.assertEqual(
            TestResult.SUCCESS,
            converter.to_test(Mock(), case).result
        )

        case.skipped = Mock()
        case.failure = None

        self.assertEqual(
            TestResult.SKIPPED,
            converter.to_test(Mock(), case).result
        )

        case.skipped = None
        case.failure = Mock()

        self.assertEqual(
            TestResult.FAILURE,
            converter.to_test(Mock(), case).result
        )

    def test_skipped_reason(self):
        """Checks conditions for the skipped reason field to be field in.
        """
        case = Mock()

        converter = XMLToTest()

        case.skipped = None

        self.assertIsNone(converter.to_test(Mock(), case).skip_reason)

        case.skipped = Mock()
        case.skipped.value = 'reason'

        self.assertEqual(
            case.skipped.value,
            converter.to_test(Mock(), case).skip_reason
        )

    def test_failure_reason(self):
        """Checks conditions for the failure reason field to be field in.
        """
        case = Mock()

        converter = XMLToTest()

        case.failure = None

        self.assertIsNone(converter.to_test(Mock(), case).failure_reason)

        case.failure = Mock()
        case.failure.value = 'reason'

        self.assertEqual(
            case.failure.value,
            converter.to_test(Mock(), case).failure_reason
        )


class TestTempestTestParser(TestCase):
    """Tests for :class:`TempestTestParser`.
    """

    @patch(
        'cibyl.sources.zuul.utils.tests.tempest.parser.download_into_memory'
    )
    @patch(
        'cibyl.sources.zuul.utils.tests.tempest.parser.get_url_to_build_file'
    )
    def test_parse_tests_at(self, urls, download):
        """Checks that the class is capable of downloading and parsing the
        test results file.
        """
        expected = Mock()

        url = 'url'
        contents = Mock()

        file = Mock()
        session = Mock()

        build = Mock()
        build.session.session = session

        suite = Mock()

        xml = Mock()
        xml.from_string = Mock()
        xml.from_string.return_value = suite

        converter = Mock()
        converter.to_suite = Mock()
        converter.to_suite.return_value = expected

        tools = Mock()
        tools.parser = xml
        tools.converter = converter

        urls.return_value = url
        download.return_value = contents

        parser = TempestTestParser(tools=tools)

        result = parser.parse_tests_at(build, file)

        self.assertEqual([expected], result)

        urls.assert_has_calls([call(build, file), call(build, file)])
        download.assert_called_once_with(url, session)
        xml.from_string.assert_called_once_with(contents, XMLTempestTestSuite)
        converter.to_suite.assert_called_once_with(url=url, suite=suite)
