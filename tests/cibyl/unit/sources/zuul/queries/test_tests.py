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

from cibyl.sources.zuul.queries.tests import perform_tests_query


class TestPerformTestsQuery(TestCase):
    """Tests for :func:`perform_tests_query`.
    """

    def test_name_filter(self):
        """Checks that filtering by name is applied if the adequate argument
        is passed.
        """
        name = 'test'

        expected = [Mock()]

        arg = Mock()
        arg.value = [name]

        kwargs = {'tests': arg}

        request = Mock()
        request.with_name = Mock()
        request.get = Mock()
        request.get.return_value = expected

        build = Mock()
        build.tests = Mock()
        build.tests.return_value = request

        result = perform_tests_query(build, **kwargs)

        self.assertEqual(expected, result)

        request.with_name.assert_called_once_with(name)
        request.get.assert_called_once()

    def test_status_filter(self):
        """Checks that filtering by name is applied if the adequate argument
        is passed.
        """
        status = 'SUCCESS'

        expected = [Mock()]

        arg = Mock()
        arg.value = [status]

        kwargs = {'test_result': arg}

        request = Mock()
        request.with_status = Mock()
        request.get = Mock()
        request.get.return_value = expected

        build = Mock()
        build.tests = Mock()
        build.tests.return_value = request

        result = perform_tests_query(build, **kwargs)

        self.assertEqual(expected, result)

        request.with_status.assert_called_once_with(status)
        request.get.assert_called_once()
