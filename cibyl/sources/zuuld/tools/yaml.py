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

from cached_property import cached_property

from cibyl.sources.zuuld.errors import IllegibleData
from cibyl.sources.zuuld.models.job import Job
from kernel.tools.files import FileSearchFactory
from kernel.tools.fs import Dir, File
from kernel.tools.json import Draft7ValidatorFactory, JSONValidatorFactory
from kernel.tools.yaml import YAML, StandardYAMLParser, YAMLArray, YAMLParser


class YAMLReader:
    DEFAULT_SCHEMA = File('_data/schemas/zuuld.json')

    @dataclass
    class Tools:
        parser: YAMLParser = field(
            default_factory=lambda *_: StandardYAMLParser()
        )
        validators: JSONValidatorFactory = field(
            default_factory=lambda *_: Draft7ValidatorFactory()
        )

    def __init__(
        self,
        file: File,
        schema: Optional[File] = None,
        tools: Optional[Tools] = None
    ):
        if schema is None:
            schema = YAMLReader.DEFAULT_SCHEMA

        if tools is None:
            tools = YAMLReader.Tools()

        self._file = file
        self._schema = schema
        self._tools = tools

    @cached_property
    def data(self) -> YAML:
        data = self.tools.parser.as_yaml(self.file.read())
        validator = self.tools.validators.from_file(self.schema)

        if not validator.is_valid(data):
            raise IllegibleData()

        return data

    @property
    def file(self) -> File:
        return self._file

    @property
    def schema(self) -> File:
        return self._schema

    @property
    def tools(self) -> Tools:
        return self._tools

    def jobs(self) -> Iterable[Job]:
        def jobs() -> YAMLArray:
            return [entry['job'] for entry in self.data if 'job' in entry]

        result = []

        for job in jobs():
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


class YAMLReaderFactory:
    """Factory for :class:`YAMLReader`.
    """

    def from_file(self, file: File) -> YAMLReader:
        return YAMLReader(file)


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

        return [File(path) for path in search.get()]
