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

from cibyl.sources.zuul.api import ZuulAPIError
from cibyl.sources.zuul.client import ZuulClient, ZuulClientError


class TestClient(TestCase):
    """Test cases for :class:`ZuulClient`.
    """

    def test_connect_throws_error_on_failed_request(self):
        """Checks that a :class:`ZuulClientError` is raised if no connection
        can be made with the host.
        """

        def raise_api_error():
            raise ZuulAPIError

        api = Mock()
        api.info = Mock()
        api.info.side_effect = raise_api_error

        client = ZuulClient(api)

        self.assertRaises(ZuulClientError, client.connect)
