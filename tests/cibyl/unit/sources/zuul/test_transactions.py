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
from unittest.mock import Mock

from parameterized import parameterized

from cibyl.cli.ranged_argument import Range
from cibyl.models.ci.zuul.test import TestKind, TestStatus
from cibyl.sources.zuul.transactions import (TestResponse, TestsRequest,
                                             VariantResponse)
from cibyl.sources.zuul.utils.tests.tempest.types import TempestTest
from cibyl.sources.zuul.utils.tests.types import Test, TestResult


class TestTestsRequest(TestCase):
    """Tests for :class:`TestsRequest`.
    """

    def test_with_name(self):
        """Checks that the request can filter tests by name.
        """
        test1 = Mock()
        test1.name = 'test1'

        test2 = Mock()
        test2.name = 'test2'

        suite = Mock()
        suite.tests = [test1, test2]

        build = Mock()
        build.tests = Mock()
        build.tests.return_value = [suite]

        name = test1.name

        request = TestsRequest(build)
        request.with_name(name)

        result = list(request.get())

        self.assertEqual(1, len(result))
        self.assertEqual(test1, result[0].data)

    @parameterized.expand(['SUCCESS', 'success'])
    def test_with_status(self, status: str):
        """Checks that the request can filter tests by status.
        """
        test1 = Mock()
        test1.name = 'test1'
        test1.result = TestResult.SUCCESS

        test2 = Mock()
        test2.name = 'test2'
        test2.result = TestResult.FAILURE

        suite = Mock()
        suite.tests = [test1, test2]

        build = Mock()
        build.tests = Mock()
        build.tests.return_value = [suite]

        request = TestsRequest(build)
        request.with_status(status)

        result = list(request.get())

        self.assertEqual(1, len(result))
        self.assertEqual(TestStatus.SUCCESS, result[0].status)

    def test_with_duration(self):
        """Checks that the request can filter tests by duration.
        """
        test1 = Mock()
        test1.name = 'test1'
        test1.duration = 10

        test2 = Mock()
        test2.name = 'test2'
        test2.duration = 2

        suite = Mock()
        suite.tests = [test1, test2]

        build = Mock()
        build.tests = Mock()
        build.tests.return_value = [suite]

        duration = Range('>', 2)

        request = TestsRequest(build)
        request.with_duration(duration)

        result = list(request.get())

        self.assertEqual(1, len(result))
        self.assertEqual(test1.name, result[0].name)


class TestVariantResponse(TestCase):
    """Tests for :class:`VariantResponse`.
    """

    def test_explicit_branches(self):
        """Checks that when the variant has explicit branches assigned to
        it, those are the ones returned.
        """
        api = Mock()
        api.branches = ['explicit']

        variant = VariantResponse(variant=api)

        self.assertEqual(api.branches, variant.branches)

    def test_implicit_branches(self):
        """Checks that when the variant has no explicit branches assigned to
        it, the branch is implicitly extracted from its definition then.
        """
        context = Mock()
        context.branch = 'implicit'

        api = Mock()
        api.branches = []
        api.context = context

        variant = VariantResponse(variant=api)

        self.assertEqual([context.branch], variant.branches)


class TestTestResponse(TestCase):
    """Tests for :class:`TestResponse`.
    """

    def test_kind(self):
        """Checks that the correct test types are returned.
        """
        generic_test = Mock(spec=Test)
        tempest_test = Mock(spec=TempestTest)

        response = TestResponse(Mock(), Mock(), generic_test)

        self.assertEqual(TestKind.UNKNOWN, response.kind)

        response = TestResponse(Mock(), Mock(), tempest_test)

        self.assertEqual(TestKind.TEMPEST, response.kind)

    def test_status(self):
        """Checks that the correct result is returned.
        """
        test = Mock()

        response = TestResponse(Mock(), Mock(), test)

        test.result = TestResult.SUCCESS

        self.assertEqual(TestStatus.SUCCESS, response.status)

        test.result = TestResult.FAILURE

        self.assertEqual(TestStatus.FAILURE, response.status)

        test.result = TestResult.SKIPPED

        self.assertEqual(TestStatus.SKIPPED, response.status)

        test.result = TestResult.UNKNOWN

        self.assertEqual(TestStatus.UNKNOWN, response.status)
