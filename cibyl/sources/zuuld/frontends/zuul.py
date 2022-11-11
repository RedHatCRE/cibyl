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

from cibyl.sources.zuul.apis import ZuulAPI, ZuulTenantAPI, ZuulJobAPI
from cibyl.sources.zuuld.errors import UnsupportedError


class _Job(ZuulJobAPI):
    @property
    @overrides
    def url(self):
        raise UnsupportedError

    @overrides
    def variants(self):
        raise UnsupportedError

    @overrides
    def builds(self):
        raise UnsupportedError

    @overrides
    def close(self):
        return


class _Tenant(ZuulTenantAPI):
    @overrides
    def projects(self):
        raise UnsupportedError

    @overrides
    def jobs(self):
        raise UnsupportedError

    @overrides
    def builds(self):
        raise UnsupportedError

    @overrides
    def close(self):
        return


class ZuulFrontend(ZuulAPI):
    @overrides
    def info(self):
        raise UnsupportedError

    @overrides
    def tenants(self):
        raise UnsupportedError

    @overrides
    def close(self):
        return
