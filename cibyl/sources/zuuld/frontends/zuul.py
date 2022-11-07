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
from overrides import overrides

from cibyl.sources.zuul.apis import ZuulAPI
from cibyl.sources.zuul.apis.factories import ZuulAPIFactory


class ZuulFrontend(ZuulAPI):
    @overrides
    def info(self):
        return {}

    @overrides
    def tenants(self):
        return []

    @overrides
    def close(self) -> None:
        return


class ZuulFrontendFactory(ZuulAPIFactory):
    @overrides
    def create(self, url, cert=None, **kwargs) -> ZuulFrontend:
        return ZuulFrontend()
