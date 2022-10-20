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
from abc import ABC, abstractmethod
from typing import Any, Dict

Query = Dict[str, Any]
"""Type for arguments of the query to by run by the source."""


class QueryModifier(ABC):
    """Interface for all classes that alter query arguments in order to
    extend or reduce the scope of a query based on some conditionals.
    """

    @abstractmethod
    def modify(self, **kwargs) -> Query:
        """Alters the query represented by the keyword arguments.

        :param kwargs: Arguments describing the query.
        :return: The same query, modified by this class under its criteria.
        """
        raise NotImplementedError
