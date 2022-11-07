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

from cibyl.sources.zuul.apis import ZuulAPI
from cibyl.sources.zuul.apis.factories import ZuulAPIFactory
from cibyl.sources.zuul.apis.rest import ZuulRESTClient
from kernel.tools.urls import URL


class ZuulRESTFactory(ZuulAPIFactory):
    """Factory that provides interfaces with a Zuul host through the use of
    the host's REST-API.
    """

    def __init__(self, url: URL, cert: Optional[str] = None):
        self._url = url
        self._cert = cert

    @staticmethod
    def from_kwargs(**kwargs):
        if 'url' not in kwargs:
            raise ValueError

        return ZuulRESTFactory(
            url=kwargs['url'],
            cert=kwargs.get('cert')
        )

    @property
    def url(self) -> URL:
        return self._url

    @property
    def cert(self) -> Optional[str]:
        return self._cert

    @overrides
    def new(self) -> ZuulAPI:
        return ZuulRESTClient.from_url(
            host=self.url,
            cert=self.cert
        )
