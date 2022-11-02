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
from pathlib import Path
from typing import Iterable, Optional

from overrides import overrides

from cibyl.sources.zuuld.errors import IllegibleData
from cibyl.sources.zuuld.models.job import Job
from cibyl.sources.zuuld.scms.git import GitStorage
from kernel.scm.git.apis.cli import Repository
from kernel.tools.fs import File
from kernel.tools.io import Closeable
from kernel.tools.json import Draft7ValidatorFactory, JSONValidatorFactory
from kernel.tools.yaml import YAML, StandardYAMLParser, YAMLParser


class YAMLHandle:
    DEFAULT_SCHEMA_FILE = File('_data/schemas/zuuld.json')

    @dataclass
    class Tools:
        validators: JSONValidatorFactory = field(
            default_factory=lambda *_: Draft7ValidatorFactory()
        )

    def __init__(
        self,
        data: YAML,
        schema: Optional[File] = None,
        tools: Optional[Tools] = None
    ):
        if schema is None:
            schema = YAMLHandle.DEFAULT_SCHEMA_FILE

        if tools is None:
            tools = YAMLHandle.Tools()

        self._raw = data
        self._schema = schema
        self._tools = tools

        if not self._is_valid():
            raise IllegibleData(
                f"Data does not conform to schema at: '{self.schema}'"
            )

    @property
    def raw(self) -> YAML:
        return self._raw

    @property
    def schema(self) -> File:
        return self._schema

    @property
    def tools(self) -> Tools:
        return self._tools

    def _is_valid(self) -> bool:
        validator = self.tools.validators.from_file(self.schema)

        return validator.is_valid(self.raw)

    def read_jobs(self) -> Iterable[Job]:
        result = []

        for job in self._raw:
            model = Job(
                name=job['name']
            )

            if 'parent' in job:
                model.parent = job['parent']

            if 'branches' in job:
                branches = job['branches']

                if isinstance(branches, str):
                    branches = [branches]

                model.branches = branches

            if 'vars' in job:
                model.vars = job['vars']

            result.append(model)

        return result


class FileHandle:
    @dataclass
    class Tools:
        yaml: YAMLParser = field(
            default_factory=lambda *_: StandardYAMLParser()
        )

    def __init__(self, handle: File, tools: Optional[Tools] = None):
        if tools is None:
            tools = FileHandle.Tools()

        self._handle = handle
        self._tools = tools

    @property
    def handle(self) -> File:
        return self._handle

    @property
    def tools(self) -> Tools:
        return self._tools

    def as_yaml(self) -> YAMLHandle:
        return YAMLHandle(
            data=self.tools.yaml.as_yaml(self.handle.read())
        )


class RepositoryHandle(Closeable):
    def __init__(self, handle: Repository):
        self._handle = handle

    @property
    def handle(self) -> Repository:
        return self._handle

    @overrides
    def close(self):
        self.handle.close()

    def files_at(self, path: Path) -> Iterable[FileHandle]:
        workspace = self.handle.workspace

        directory = workspace.cd(path)
        directory.check_exists()

        result = []

        for element in directory.ls():
            if not isinstance(element, File):
                continue

            file = FileHandle(handle=element)
            result.append(file)

        return result


class GitBackend(Closeable):
    @dataclass
    class DatabaseEntry:
        handle: RepositoryHandle
        directory: Path

    RepositoryDB = Iterable[DatabaseEntry]

    def __init__(self, db: RepositoryDB):
        self._db = db

    @property
    def db(self) -> RepositoryDB:
        return self._db

    @overrides
    def close(self):
        for entry in self.db:
            entry.handle.close()


class GitBackendFactory:
    def from_defs(self, defs: Iterable[GitStorage]) -> GitBackend:
        pass
