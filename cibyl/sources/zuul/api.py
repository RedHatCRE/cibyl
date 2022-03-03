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
import logging

from zuulclient.api import ZuulRESTClient

LOG = logging.getLogger(__name__)


class ZuulAPIError(Exception):
    """Represents an error occurring during the execution of an operation over
    the target host.
    """


def safe_request(request):
    """Decorator that wraps any errors coming out of a call around a
    :class:`ZuulAPIError`.

    :param request: The unsafe call to watch errors on.
    :return: The input call decorated to raise the desired error type.
    """

    def request_handler(*args):
        """Calls the unsafe function and wraps any errors coming out of it
        around a :class:`ZuulAPIError`.

        :param args: Arguments with which the function is called.
        :return: Output of the called function.
        """
        try:
            return request(*args)
        except Exception as ex:
            raise ZuulAPIError('Failure on request to target host.') from ex

    return request_handler


class ZuulAPI:
    """Provides a low-level client to interact with Zuul's REST-API.
    """

    def __init__(self, client):
        """Constructor.
        This constructor is not meant to be called directly, please refer to
        the static constructors before.

        :param client: A REST-API client to communicate with the host through.
        :type client: :class:`zuulclient.api.ZuulRESTClient`
        """
        self._client = client

    @staticmethod
    def from_url(url, cert=None, auth_token=None):
        """Builds an API from the parameters that define the connection to
        the target host.

        :param url: URL where the host is located.
        :type url: str
        :param cert: Path to the certificate that identifies the host. 'None'
            will disable authentication of the host, not recommended in
            production environments as it allows man-in-the-middle attacks
            to be made.
        :type cert: None or str
        :param auth_token: Token used to perform admin operations. 'None'
            will simply not allow such operations to be performed.
        :type auth_token: None or str
        :return: The built instance.
        :rtype: :class:`ZuulAPI`
        """
        # Host is not verified by default
        verify = False

        # Check if a certificate to do so has been provided
        if cert:
            verify = cert

        return ZuulAPI(ZuulRESTClient(url, verify, auth_token))

    @property
    def url(self):
        """
        :return: The host's URL.
        :rtype: str
        """
        return self._client.url

    @property
    def cert(self):
        """
        :return: Path to the certificate that authenticates the host.
        :rtype: None or str
        """
        verify = self._client.verify

        if isinstance(verify, str):
            return verify

        return None

    @property
    def auth_token(self):
        """
        :return: Authentication token used to perform admin tasks.
        :rtype: None or str
        """
        return self._client.auth_token

    @safe_request
    def info(self):
        """Gets Zuul's info data, containing information about capabilities
        and tenants

        :return: The JSON structure returned by the host.
        :rtype: dict
        """
        return self._client.info
