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
from typing import Iterable

from overrides import overrides

from cibyl.sources.zuuld.backends.abc import T, ZuulDBackend
from cibyl.sources.zuuld.models.job import Job

LOG = logging.getLogger(__name__)


class AggregatedBackend(ZuulDBackend[T]):
    class Get(ZuulDBackend.Get):
        def __init__(self, backends: Iterable[ZuulDBackend.Get]):
            self._backends = backends

        @property
        @overrides
        def name(self):
            # Example: Aggregated -> (2){GitHub, Git}
            # Where:
            #   -> The number is the amount of backends in the aggregation.
            #   -> The list between {} are the names of the backends.
            result = "Aggregated -> "
            result += f'({sum(1 for _ in self.backends)})'
            result += "{"
            result += ", ".join(backend.name for backend in self.backends)
            result += "}"

            return result

        @property
        def backends(self) -> Iterable[ZuulDBackend.Get]:
            return self._backends

        @overrides
        def jobs(self, spec: T) -> Iterable[Job]:
            for backend in self.backends:
                LOG.debug("Fetching jobs through backend: '%s'.", backend.name)
                try:
                    return backend.jobs(spec)
                except ZuulDBackend as ex:
                    LOG.debug("Failed to fetch jobs due to error: '%s'.", ex)
                    continue

    def __init__(self, get: Iterable[ZuulDBackend[T].Get]):
        super().__init__(
            get=AggregatedBackend.Get(
                backends=get
            )
        )
