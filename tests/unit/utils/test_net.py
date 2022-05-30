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

from cibyl.utils.net import DownloadError, download_into_memory, requests


class TestDownloadIntoMemory(TestCase):
    """Tests for :func:`download_into_memory`.
    """

    def test_raises_error_for_bad_errorcode(self):
        """Checks that an error is raised if the request returned an error
        code.
        """
        response = Mock()
        response.ok = False

        requests.get = Mock()
        requests.get.return_value = response

        with self.assertRaises(DownloadError):
            download_into_memory('https://localhost:8080')

    def test_gets_url_contents(self):
        """Checks that the contents of the page are returned as a string.
        """
        url = 'https://localhost:8080'
        string = 'HELLO'
        content = bytearray(string, 'utf-8')

        response = Mock()
        response.ok = True
        response.content = content

        requests.get = Mock()
        requests.get.return_value = response

        self.assertEqual(string, download_into_memory(url))

        requests.get.assert_called_once_with(url)

    def test_uses_session(self):
        """Checks that if a session is passed, that is used instead.
        """
        url = 'https://localhost:8080'
        string = 'HELLO'
        content = bytearray(string, 'utf-8')

        response = Mock()
        response.ok = True
        response.content = content

        session = Mock()
        session.get = Mock()
        session.get.return_value = response

        self.assertEqual(string, download_into_memory(url, session))

        session.get.assert_called_once_with(url)
