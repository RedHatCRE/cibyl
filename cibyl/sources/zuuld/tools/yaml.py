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
from kernel.tools.fs import Dir, File, KnownDirs, cd
from kernel.tools.json import Draft7ValidatorFactory
from kernel.tools.yaml import YAMLArray, YAMLError, YAMLFile

LOG = logging.getLogger(__name__)


class ZuulDFile(YAMLFile):
    """Representation of a YAML file that meets the Zuul.D schema.
    """
    SCHEMA = File('_data/schemas/zuuld.json')
    """Location of the Zuul.D schema."""

    def __init__(self, file: File, tools: Optional[YAMLFile.Tools] = None):
        """Constructor.

        :param file: File to test against the Zuul.D schema.
        :param tools: Tools this uses to do its task.
        :raises YAMLError: If the file does not meet the schema.
        """
        with cd(KnownDirs.CIBYL):
            validators = Draft7ValidatorFactory()

            super().__init__(
                file=file,
                validator=validators.from_file(ZuulDFile.SCHEMA),
                tools=tools
            )


class ZuulDFileFactory:
    """Factory for :class:`ZuulDFile`.
    """

    def from_file(self, file: File) -> ZuulDFile:
        """Builds a new Zuul.D file from a generic one.

        :param file: File that will be tested to see if it is a Zuul.D file.
        :return: The given file, this time caster to a Zuul.D one.
        :raises YAMLError: If the file does not meet the Zuul.D criteria.
        """
        return ZuulDFile(file)


class YAMLReader:
    """Parses the contents of a Zuul.D file.
    """

    class DataExtractor:
        """Utility class used to extract YAML data from a Zuul.D file.
        """

        def __init__(self, file: ZuulDFile):
            """Constructor.

            :param file: The file to get the data from.
            """
            self._file = file

        @property
        def file(self) -> ZuulDFile:
            """
            :return: File this class is extracting data from.
            """
            return self._file

        def jobs(self) -> YAMLArray:
            """
            :return: All 'job' entries found on the file.
            """
            return [entry['job'] for entry in self.file.data if 'job' in entry]

    def __init__(self, file: ZuulDFile):
        """Constructor.

        :param file: The file to parse.
        """
        self._data = YAMLReader.DataExtractor(file)

    @property
    def file(self) -> ZuulDFile:
        """
        :return: The file this class is parsing.
        """
        return self._data.file

    def jobs(self) -> Iterable[Job]:
        """Parses all job entries on the file and returns a python
        representation for each of them.

        :return: Model for each job entry on the file.
        """
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
        """Builds a new reader from a Zuul.D file.

        :param file: The Zuul.D file.
        :return: The reader instance.
        """
        return YAMLReader(file)


class YAMLSearch:
    """Recursively looks for Zuul.D YAML files on a directory.

    The class crawls first through a directory in search of generic YAML
    files to test. Then, it checks each one in order to look for those
    that can be considered Zuul.D compliant and finally returns those.

    A Zuul.D compliant YAML file are those files that meet the Zuul.D schema.
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
        """Used to go from a generic YAML file to a Zuul.D compliant one."""

    def __init__(
        self,
        extensions: Optional[Iterable[str]] = None,
        tools: Optional[Tools] = None
    ):
        """Constructor.

        :param extensions:
            File extensions that identify YAML files.
            These point to all files on a directory that are to be
            checked for Zuul.D contents.
            Consequently, files identified by these extensions may, or not, be
            Zuul.D compliant.
            'None' to use the default set: YAMLReader.DEFAULT_YAML_EXTENSIONS.
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
        :return: File extensions the class looks for.
        """
        return self._extensions

    @property
    def tools(self) -> Tools:
        """
        :return: Tools used by the class to do its job.
        """
        return self._tools

    def search(self, path: Dir) -> Iterable[ZuulDFile]:
        """Recursively searches the directory for all Zuul.D YAML files on it.

        :param path: Directory to look in.
        :return: A handle to all found files.
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
                continue

        return result

    def _search_for_yamls_at(self, path: Dir) -> Iterable[File]:
        """Recursively looks for all YAML files on a directory.

        :param path: Directory to look in.
        :return: A handle to all found files.
        """
        search = self.tools.searches.from_root(path)
        search.with_recursion()

        for ext in self.extensions:
            search.with_extension(ext)

        return [File(find) for find in search.get()]
