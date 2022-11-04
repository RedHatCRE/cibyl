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
from dataclasses import dataclass, field
from typing import Iterable, Optional

from overrides import overrides

from cibyl.sources.zuuld.backends.abc import T, ZuulDBackend
from cibyl.sources.zuuld.models import Job
from cibyl.sources.zuuld.specs.git import GitSpec
from kernel.scm.git.tools.cloning import RepositoryFactory


class GitBackend(ZuulDBackend[GitSpec]):
    class Get(ZuulDBackend.Get):
        @dataclass
        class Tools:
            repositories: RepositoryFactory = field(
                default_factory=lambda *_: RepositoryFactory()
            )

        def __init__(self, tools: Optional[Tools] = None):
            if tools is None:
                tools = GitBackend.Get.Tools()

            self._tools = tools

        @property
        def tools(self) -> Tools:
            return self._tools

        @overrides
        def jobs(self, spec: T) -> Iterable[Job]:
            repo = self.tools.repositories.from_remote(url=spec.remote)

            return []

    def __init__(self):
        super().__init__(get=GitBackend.Get())
