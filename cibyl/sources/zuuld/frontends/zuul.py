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
from dataclasses import dataclass
from typing import Dict, Generic, Iterable

from overrides import overrides

from cibyl.sources.zuul.apis import ZuulAPI, ZuulJobAPI, ZuulTenantAPI
from cibyl.sources.zuuld.backends.abc import T, ZuulDBackend
from cibyl.sources.zuuld.errors import UnsupportedError


@dataclass
class Session(Generic[T]):
    specs: Iterable[T]
    backend: ZuulDBackend[T]


class _Job(Generic[T], ZuulJobAPI):
    def __init__(
        self,
        session: Session[T],
        spec: T,
        tenant: '_Tenant',
        job: Dict
    ):
        super().__init__(tenant, job)

        self._session = session
        self._spec = spec

    @property
    def session(self) -> Session[T]:
        return self._session

    @property
    def spec(self) -> T:
        return self._spec

    @property
    @overrides
    def url(self):
        return self.spec.remote

    @overrides
    def variants(self):
        raise UnsupportedError

    @overrides
    def builds(self):
        raise UnsupportedError

    @overrides
    def close(self):
        return


class _Tenant(Generic[T], ZuulTenantAPI):
    def __init__(self, session: Session[T], data: Dict):
        super().__init__(data)

        self._session = session

    @property
    def session(self) -> Session[T]:
        return self._session

    @property
    def _specs(self) -> Iterable[T]:
        return self._session.specs

    @property
    def _backend(self) -> ZuulDBackend[T]:
        return self._session.backend

    @overrides
    def projects(self):
        raise UnsupportedError

    @overrides
    def jobs(self):
        result = []

        for spec in self._specs:
            for job in self._backend.get.jobs(spec):
                result.append(
                    _Job[T](
                        session=self.session,
                        spec=spec,
                        tenant=self,
                        job={
                            'name': job.name
                        }
                    )
                )

        return result

    @overrides
    def builds(self):
        raise UnsupportedError

    @overrides
    def close(self):
        return


class ZuulFrontend(Generic[T], ZuulAPI):
    def __init__(self, session: Session[T]):
        self._session = session

    @property
    def session(self) -> Session[T]:
        return self._session

    @overrides
    def info(self):
        raise UnsupportedError

    @overrides
    def tenants(self):
        return [
            _Tenant[T](
                session=self.session,
                data={
                    'name': 'zuul.d'
                }
            )
        ]

    @overrides
    def close(self):
        return
