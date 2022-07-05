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
from unittest.mock import Mock, patch

from tripleo.utils.urls import URL


class TestURL(TestCase):
    """Tests for :class:`URL`.
    """

    @patch('tripleo.utils.urls.is_url')
    def test_new_on_valid_url(self, check_mock: Mock):
        """Checks that if the string is a URL, the string is created.
        """
        string = 'some-string-that-is-a-url'

        check_mock.return_value = True

        self.assertEqual(string, URL(string))

        check_mock.assert_called_once_with(string)

    @patch('tripleo.utils.urls.is_url')
    def test_error_on_invalid_url(self, check_mock: Mock):
        """Checks that if the string is not a URL, an error is thrown.
        """
        string = 'some-string-that-is-no-url'

        check_mock.return_value = False

        with self.assertRaises(ValueError):
            URL(string)

        check_mock.assert_called_once_with(string)

    @patch('tripleo.utils.urls.is_url')
    def test_trims_string(self, check_mock: Mock):
        """Checks that before verifying the string, it is trimmed first.
        """
        string = 'some-string-that-is-a-url'
        broken_string = f'{string}  '

        check_mock.return_value = True

        self.assertEqual(string, URL(broken_string))

        check_mock.assert_called_once_with(string)
