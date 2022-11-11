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
from typing import Generic, TypeVar

from cibyl.sources.zuul.apis import ZuulAPI

T = TypeVar('T', bound=ZuulAPI)
"""Type for APIs built by the factory."""


class ZuulAPIFactory(Generic[T], ABC):
    """Base class for factories that create instances for subclasses of
    :class:`ZuulAPI`.
    """

    @abstractmethod
    def new(self) -> T:
        """Builds a new instance of the API.

        :return: The new instance.
        """
        raise NotImplementedError
