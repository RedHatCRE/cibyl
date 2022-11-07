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
from pathlib import Path
from typing import Generic, Iterable

from overrides import overrides

from cibyl.sources.zuul.apis import ZuulAPI, ZuulJobAPI, ZuulTenantAPI
from cibyl.sources.zuul.apis.factories import ZuulAPIFactory
from cibyl.sources.zuuld.backends.abc import T as SPEC_T
from cibyl.sources.zuuld.backends.abc import ZuulDBackend
from cibyl.sources.zuuld.backends.git import GitBackend
from cibyl.sources.zuuld.models.job import Job
from cibyl.sources.zuuld.specs.git import GitSpec
from kernel.tools.urls import URL
from kernel.tools.yaml import YAML


class SpecWorker(Generic[SPEC_T]):
    def __init__(self, spec: SPEC_T, backend: ZuulDBackend[SPEC_T]):
        self._spec = spec
        self._backend = backend

    def jobs(self) -> Iterable[Job]:
        return self._backend.get.jobs(self._spec)


class JobAPI(ZuulJobAPI):
    @property
    @overrides
    def url(self):
        return ''

    @overrides
    def variants(self):
        raise NotImplementedError

    @overrides
    def builds(self):
        raise NotImplementedError

    @overrides
    def close(self) -> None:
        return


class TenantAPI(ZuulTenantAPI):
    def __init__(
        self,
        workers: Iterable[SpecWorker],
        data: YAML
    ):
        super().__init__(tenant=data)

        self._workers = workers

    @overrides
    def projects(self):
        raise NotImplementedError

    @overrides
    def jobs(self):
        result = []

        for worker in self._workers:
            result += [
                JobAPI(tenant=self, job={'name': job.name})
                for job in worker.jobs()
            ]

        return result

    @overrides
    def builds(self):
        raise NotImplementedError

    @overrides
    def close(self) -> None:
        return


class ZuulFrontend(ZuulAPI):
    def __init__(self, workers: Iterable[SpecWorker]):
        self._workers = workers

    @overrides
    def info(self):
        raise NotImplementedError

    @overrides
    def tenants(self):
        return [
            TenantAPI(
                workers=self._workers,
                data={'name': 'zuul.d'}
            )
        ]

    @overrides
    def close(self) -> None:
        return


class ZuulFrontendFactory(ZuulAPIFactory):
    def __init__(self, workers: Iterable[SpecWorker]):
        self._workers = workers

    @staticmethod
    def from_kwargs(**kwargs) -> 'ZuulFrontendFactory':
        if 'repos' not in kwargs:
            raise ValueError

        workers = []

        for repo in kwargs['repos']:
            workers.append(
                SpecWorker(
                    spec=GitSpec(
                        remote=URL(repo['url']),
                        directory=Path('zuul.d/')
                    ),
                    backend=GitBackend()
                )
            )

        return ZuulFrontendFactory(workers)

    @overrides
    def new(self) -> ZuulAPI:
        return ZuulFrontend(workers=self._workers)
