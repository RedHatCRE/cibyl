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
from unittest.mock import Mock, PropertyMock

from cibyl.sources.zuul.api import ZuulAPI, ZuulAPIError, safe_request


class TestSafeRequest(TestCase):
    """Tests for :func:`safe_request`.
    """

    def test_wraps_errors(self):
        """Tests that errors coming out of the call are wrapped around the
        API's error type.
        """

        @safe_request
        def request():
            raise Exception

        self.assertRaises(ZuulAPIError, request)

    def test_returns_result_when_no_error(self):
        """Tests that the call's output is returned when everything goes right.
        """
        result = {'some_key': 'some_value'}

        @safe_request
        def request():
            return result

        self.assertEqual(result, request())


class TestZuulAPIFromUrl(TestCase):
    """Tests for :meth:`ZuulAPI.from_url`.
    """

    def test_with_all_args(self):
        """Checks that the object is built correctly when all arguments are
        provided.
        """
        url = 'url/to/zuul/'
        cert = 'path/to/cert.pem'
        auth_token = 'token'

        api = ZuulAPI.from_url(url, cert, auth_token)

        self.assertEqual(url, api.url)
        self.assertEqual(cert, api.cert)
        self.assertEqual(auth_token, api.auth_token)

    def test_with_no_cert(self):
        """Checks that object is built correctly when the certificate is not
        provided.
        """
        url = 'url/to/zuul/'
        cert = None
        auth_token = 'token'

        api = ZuulAPI.from_url(url, cert, auth_token)

        self.assertEqual(url, api.url)
        self.assertEqual(None, api.cert)
        self.assertEqual(auth_token, api.auth_token)


class TestZuulAPI(TestCase):
    """Tests for :class:`ZuulAPI`.
    """

    def test_info(self):
        """Tests that the correct info from :meth:`ZuulAPI.info` is
        retrieved.
        """
        client = Mock()
        client.info = PropertyMock()

        api = ZuulAPI(client)

        self.assertEqual(client.info, api.info())
