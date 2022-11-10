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
from typing import Optional

from overrides import overrides

from cibyl.sources.zuul.apis.factories.abc import ZuulAPIFactory
from cibyl.sources.zuul.apis.rest import ZuulRESTClient
from kernel.tools.urls import URL


class ZuulRESTClientFactory(ZuulAPIFactory[ZuulRESTClient]):
    """Factory for :class:`ZuulRESTClient`.
    """

    def __init__(self, host: URL, cert: Optional[str] = None):
        """Constructor.

        :param host: Address of the Zuul host the API will interact with.
        :param cert: See :meth:`ZuulRESTClient.from_url`
        """
        self._host = host
        self._cert = cert

    @property
    def host(self) -> URL:
        """
        :return: Address of the Zuul host the API will interact with.
        """
        return self._host

    @property
    def cert(self) -> Optional[str]:
        """
        :return: Path to the certificate that authenticates the user.
        """
        return self._cert

    @overrides
    def new(self) -> ZuulRESTClient:
        return ZuulRESTClient.from_url(
            host=self.host,
            cert=self.cert
        )
