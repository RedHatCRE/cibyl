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
from typing import Generic, Iterable

from overrides import overrides

from cibyl.sources.zuuld.backends.abc import T, ZuulDBackend
from cibyl.sources.zuuld.models.job import Job

LOG = logging.getLogger(__name__)


class AggregatedBackend(Generic[T], ZuulDBackend[T]):
    """Implementation of a Zuul.D backend meant to combine other
    implementations into a single one so that, in the case one fails, others
    can try stepping up to the task.

    All implementation aggregated here must support the same type of spec
    as indicated by the generic argument. This means, for example, that for
    Git specs, only Git backends may be aggregated here.
    """

    class Get(ZuulDBackend.Get):
        """Iterates over the aggregated backends to read data from a spec.
        """

        def __init__(self, backends: Iterable[ZuulDBackend.Get]):
            """Constructor.

            :param backends:
                Backends this will iterate through.
                Container type is important, as it will decide order of
                iteration over the elements.
                In case a backend fails during an operation, the next one from
                this container is asked to fill in its shoes. The iteration
                continues until one is able to satisfy the request.
                Every time a request is made, the iteration is restarted and
                the first element is tried again.
            """
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
            """
            :return: Backends this provider iterates over.
            """
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
        """Constructor.

        :param get:
            Interfaces that provide reading capabilities to this backend.
            See :class:`AggregatedBackend.Get` for more information.
        """
        super().__init__(
            get=AggregatedBackend.Get(
                backends=get
            )
        )
