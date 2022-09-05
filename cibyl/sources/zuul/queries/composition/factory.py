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

from cibyl.sources.zuul.apis import ZuulAPI as Zuul
from cibyl.sources.zuul.output import QueryOutputMode
from cibyl.sources.zuul.queries.composition.quick import QuickQuery
from cibyl.sources.zuul.queries.composition.verbose import VerboseQuery

LOG = logging.getLogger(__name__)


class AggregatedQueryFactory:
    """Factory for :class:`AggregatedQuery`.
    """

    def from_kwargs(self, api: Zuul, **kwargs):
        """Infers the desired query type from the undefined arguments passed
        here.

        :param api: Low-Level API with which to interact with the Zuul host.
        :param kwargs: Random set of arguments.
        :return: The query instance.
        """
        arg = kwargs.get('mode')

        if not arg:
            msg = "'mode' argument is missing. Defaulting to quick query..."
            LOG.warning(msg)
            return QuickQuery(api)

        mode = QueryOutputMode.from_key(arg)

        if mode == QueryOutputMode.NORMAL:
            return QuickQuery(api)

        if mode == QueryOutputMode.VERBOSE:
            return VerboseQuery(api)

        msg = "Unknown query mode: '%s'. Defaulting to quick query..."
        LOG.warning(msg, arg)
        return QuickQuery(api)
