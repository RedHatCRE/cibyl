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
from dataclasses import dataclass, field
from typing import Iterable, Optional

from cibyl.sources.zuuld.models.job import Job
from kernel.tools.files import FileSearchFactory
from kernel.tools.fs import Dir, File
from kernel.tools.yaml import YAMLArray, YAMLError, YAMLFile

LOG = logging.getLogger(__name__)


class ZuulDFile(YAMLFile):
    SCHEMA = File('_data/schemas/zuuld.json')

    def __init__(self, file: File, tools: Optional[YAMLFile.Tools] = None):
        super().__init__(
            file=file,
            schema=ZuulDFile.SCHEMA,
            tools=tools
        )


class ZuulDFileFactory:
    def from_file(self, file: File) -> ZuulDFile:
        return ZuulDFile(file)


class YAMLReader:
    class DataExtractor:
        def __init__(self, file: ZuulDFile):
            self._file = file

        @property
        def file(self) -> ZuulDFile:
            return self._file

        def jobs(self) -> YAMLArray:
            return [entry['job'] for entry in self.file.data if 'job' in entry]

    def __init__(self, file: ZuulDFile):
        self._data = YAMLReader.DataExtractor(file)

    @property
    def file(self) -> ZuulDFile:
        return self._data.file

    def jobs(self) -> Iterable[Job]:
        result = []

        for job in self._data.jobs():
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

    def from_file(self, file: ZuulDFile) -> YAMLReader:
        return YAMLReader(file)


class YAMLSearch:
    """Recursively looks for YAML files on a directory.
    """
    DEFAULT_YAML_EXTENSIONS = ('.yml', '.yaml')
    """Default file extensions that identify YAML files."""

    @dataclass
    class Tools:
        """Tools used by the class to do its job.
        """
        searches: FileSearchFactory = field(
            default_factory=lambda *_: FileSearchFactory()
        )
        """Used to search for files of interest."""
        files: ZuulDFileFactory = field(
            default_factory=lambda *_: ZuulDFileFactory()
        )

    def __init__(
        self,
        extensions: Optional[Iterable[str]] = None,
        tools: Optional[Tools] = None
    ):
        """Constructor.

        :param extensions:
            File extensions that identify YAML files.
            'None' to use the default set: YAMLReader.DEFAULT_YAML_EXTENSIONS
        :param tools:
            Tools used by the class to do its job.
            'None' to let this build its own.
        """
        if extensions is None:
            extensions = YAMLSearch.DEFAULT_YAML_EXTENSIONS

        if tools is None:
            tools = YAMLSearch.Tools()

        self._extensions = extensions
        self._tools = tools

    @property
    def extensions(self) -> Iterable[str]:
        """
        :return: File extensions the class look for.
        """
        return self._extensions

    @property
    def tools(self) -> Tools:
        """
        :return: Tools used by this to do its task.
        """
        return self._tools

    def search(self, path: Dir) -> Iterable[ZuulDFile]:
        """Recursively searches the directory for all YAML files contained
        within.

        :param path: Directory to look in.
        :return: A handle to all retrieved files.
        """
        result = []

        for find in self._search_for_yamls_at(path):
            try:
                zuuld = self.tools.files.from_file(file=find)
                result.append(zuuld)
            except YAMLError:
                LOG.debug(
                    "Ignoring YAML file at '%(find)s' as it does not satisfy "
                    "the Zuul.D file schema.",
                    {'find': find}
                )

        return result

    def _search_for_yamls_at(self, path: Dir):
        search = self.tools.searches.from_root(path)
        search.with_recursion()

        for ext in self.extensions:
            search.with_extension(ext)

        return [File(find) for find in search.get()]
