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
from typing import Iterable, Optional

from dataclasses import dataclass, field
from overrides import overrides

from cibyl.sources.zuuld.backends.abc import T, ZuulDBackend
from cibyl.sources.zuuld.models import Job
from cibyl.sources.zuuld.specs.git import GitSpec
from kernel.scm.git.tools.cloning import RepositoryFactory
from kernel.tools.files import FileSearchFactory
from kernel.tools.fs import Dir, File


class YAMLSearch:
    DEFAULT_YAML_EXTENSIONS = ('.yml', '.yaml')

    @dataclass
    class Tools:
        files: FileSearchFactory = field(
            default_factory=lambda *_: FileSearchFactory()
        )

    def __init__(self, tools: Optional[Tools] = None):
        if tools is None:
            tools = YAMLSearch.Tools()

        self._tools = tools

    @property
    def tools(self) -> Tools:
        return self._tools

    def search(
        self,
        path: Dir,
        extensions: Optional[Iterable[str]] = None
    ) -> Iterable[File]:
        if extensions is None:
            extensions = YAMLSearch.DEFAULT_YAML_EXTENSIONS

        search = self.tools.files.from_root(path)
        search.with_recursion()

        for ext in extensions:
            search.with_extension(ext)

        return search.get()


class GitBackend(ZuulDBackend[GitSpec]):
    class Get(ZuulDBackend.Get):
        @dataclass
        class Tools:
            repositories: RepositoryFactory = field(
                default_factory=lambda *_: RepositoryFactory()
            )
            yamls: YAMLSearch = field(
                default_factory=lambda *_: YAMLSearch()
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
