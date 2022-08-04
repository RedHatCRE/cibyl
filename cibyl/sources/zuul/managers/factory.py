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
from cibyl.sources.zuul.apis import ZuulAPI as Zuul
from cibyl.sources.zuul.managers import SourceManager
from cibyl.sources.zuul.managers.verbose import VerboseManager


class SourceManagerFactory:
    """Factory for :class:`SourceManager`.
    """

    def from_kwargs(self, api: Zuul, **kwargs) -> SourceManager:
        """Chooses the manager type from the undefined arguments passed to
        this.

        :param api: Interface to communicate with the Zuul host.
        :param kwargs: Arguments coming from the CLI.
        :return: A new manager instance.
        """
        return VerboseManager(api)
