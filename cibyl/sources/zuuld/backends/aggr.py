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
from typing import Iterable

from overrides import overrides

from cibyl.sources.zuuld.backends.abc import T, ZuulDBackend
from cibyl.sources.zuuld.models.job import Job


class AggregatedBackend(ZuulDBackend[T]):
    class Get(ZuulDBackend.Get):
        def __init__(self, backends: Iterable[ZuulDBackend.Get]):
            self._backends = backends

        @property
        def backends(self) -> Iterable[ZuulDBackend.Get]:
            return self._backends

        @overrides
        def jobs(self, spec: T) -> Iterable[Job]:
            for backend in self.backends:
                try:
                    return backend.jobs(spec)
                except ZuulDBackend:
                    continue

    def __init__(self, get: Iterable[ZuulDBackend[T].Get]):
        super().__init__(
            get=AggregatedBackend.Get(
                backends=get
            )
        )
