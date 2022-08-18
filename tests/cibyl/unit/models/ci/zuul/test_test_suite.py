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

from cibyl.models.ci.zuul.test import TestStatus
from cibyl.models.ci.zuul.test_suite import TestSuite


class TestTestSuite(TestCase):
    """Tests for :class:'TestSuite'.
    """

    def test_attributes(self):
        """Checks that the model has the desired attributes.
        """
        data = TestSuite.Data()
        data.name = 'name'
        data.tests = [Mock(), Mock()]
        data.url = 'some-url'

        suite = TestSuite(data)

        self.assertEqual(data.name, suite.name.value)
        self.assertEqual(data.tests, suite.tests.value)
        self.assertEqual(data.url, suite.url.value)

    def test_equality_by_type(self):
        """Checks that the model does not match another if they are not of
        the same type.
        """
        suite = TestSuite()
        other = Mock()

        self.assertNotEqual(other, suite)

    def test_equality_by_reference(self):
        """Checks that a model is equal to itself.
        """
        suite = TestSuite()

        self.assertEqual(suite, suite)

    def test_equality_by_contents(self):
        """Checks that two suites are equal if the have the same data.
        """
        data = TestSuite.Data()
        data.name = 'name'
        data.tests = [Mock(), Mock()]
        data.url = 'some-url'

        suite1 = TestSuite(data)
        suite2 = TestSuite(data)

        self.assertEqual(suite2, suite1)

    def test_total_tests_count(self):
        """Checks that the suite reports the number of tests inside it.
        """
        data = TestSuite.Data()
        data.tests = [Mock(), Mock()]

        suite = TestSuite(data)

        self.assertEqual(2, suite.test_count)

    def test_total_success_count(self):
        """Checks that the suite reports the number of successful tests
        inside it.
        """
        test1 = Mock()
        test2 = Mock()

        test1.status = TestStatus.SUCCESS
        test2.status = TestStatus.FAILURE

        data = TestSuite.Data()
        data.tests = [test1, test2]

        suite = TestSuite(data)

        self.assertEqual(1, suite.success_count)

    def test_total_failed_count(self):
        """Checks that the suite reports the number of failed tests
        inside it.
        """
        test1 = Mock()
        test2 = Mock()

        test1.status = TestStatus.SUCCESS
        test2.status = TestStatus.FAILURE

        data = TestSuite.Data()
        data.tests = [test1, test2]

        suite = TestSuite(data)

        self.assertEqual(1, suite.failed_count)

    def test_total_skipped_count(self):
        """Checks that the suite reports the number of skipped tests
        inside it.
        """
        test1 = Mock()
        test2 = Mock()

        test1.status = TestStatus.SUCCESS
        test2.status = TestStatus.SKIPPED

        data = TestSuite.Data()
        data.tests = [test1, test2]

        suite = TestSuite(data)

        self.assertEqual(1, suite.skipped_count)

    def test_total_time(self):
        """Checks the calculated time for the test suite.
        """
        test1 = Mock()
        test2 = Mock()

        test1.duration.value = 1.0
        test2.duration.value = 3.0

        data = TestSuite.Data()
        data.tests = [test1, test2]

        suite = TestSuite(data)

        self.assertAlmostEqual(4.0, suite.total_time)

    def test_adds_test(self):
        """Checks that the suite can add a test unknown to it.
        """
        test = Mock()

        data = TestSuite.Data()

        suite = TestSuite(data)
        suite.add_test(test)

        self.assertEqual(1, len(suite.tests))
        self.assertEqual(test, suite.tests[0])

    def test_ignores_test(self):
        """Checks that if a test is already part of the suite, it is not
        added again.
        """
        test = Mock()

        data = TestSuite.Data()
        data.tests = [test]

        suite = TestSuite(data)
        suite.add_test(test)

        self.assertEqual(1, len(suite.tests))
        self.assertEqual(test, suite.tests[0])

    def test_none_if_unknown_test(self):
        """Checks that None is returned if the test is not on the suite.
        """
        suite = TestSuite()

        self.assertIsNone(suite.get_test('some_test'))

    def test_retrieves_test(self):
        """Checks that the suite is capable of fetching a test inside of it
        by name.
        """
        name = 'test'

        test = Mock()
        test.name = Mock()
        test.name.value = name

        data = TestSuite.Data()
        data.tests = [test]

        suite = TestSuite(data)

        self.assertEqual(test, suite.get_test(name))
