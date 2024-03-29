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

from cibyl.sources.zuul.apis import ZuulAPI as Zuul
from cibyl.sources.zuul.queries.modifiers import QueryModifier
from cibyl.sources.zuul.queries.modifiers.hierarchy import HierarchyModifier


class QueryModifierFactory:
    """Factory for :class:`QueryModifier`.
    """

    def from_kwargs(self, api: Zuul, **kwargs) -> Iterable[QueryModifier]:
        """Generates modifiers that react against some query
        arguments passed through the keyword arguments.

        :param api: Channel through which to communicate with the Zuul host.
        :param kwargs: Dictionary describing the query arguments passed
            through the CLI.
        :return: Modifiers resulting from the parsing of the arguments.
        """
        result = []

        if 'fetch_hierarchy' in kwargs:
            result.append(HierarchyModifier(api=api))

        return result
