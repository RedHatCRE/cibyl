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

from overrides import overrides

from cibyl.sources.zuuld.backends.abc import ZuulDBackend
from cibyl.sources.zuuld.models.job import Job
from cibyl.sources.zuuld.specs.git import GitSpec
from cibyl.sources.zuuld.tools.yaml import YAMLReaderFactory, YAMLSearch
from kernel.scm.git.tools.cloning import RepositoryFactory

LOG = logging.getLogger(__name__)


class GitBackend(ZuulDBackend[GitSpec]):
    """Implementation of a Zuul.D backend that allows interaction with Git
    repositories through Git's CLI.

    Bear in mind that this backend will require cloning of repositories and,
    as such, will need a location on the filesystem to hold that data. An
    effort is made to reduce the amount of cloning performed, but it is
    unavoidable.

    Additionally, the backend does not take care of authentication
    operations. Accessing a repository through SSH is up to the user to have
    prepared (like loading the keys...) before this is used.
    """

    class Get(ZuulDBackend.Get):
        """Clones specs and reads the information within.
        """

        @dataclass
        class Tools:
            """Tools this uses to do its task.
            """
            repositories: RepositoryFactory = field(
                default_factory=lambda *_: RepositoryFactory()
            )
            """Used to clone repositories and keep track of them."""
            files: YAMLSearch = field(
                default_factory=lambda *_: YAMLSearch()
            )
            """Used to look for Zuul.D files on the repository."""
            readers: YAMLReaderFactory = field(
                default_factory=lambda *_: YAMLReaderFactory()
            )
            """Used to parse the Zuul.D files into Python objects."""

        def __init__(self, tools: Optional[Tools] = None):
            """Constructor.

            :param tools:
                Tools this uses to do its task.
                'None' to let it build its own.
            """
            if tools is None:
                tools = GitBackend.Get.Tools()

            self._tools = tools

        @property
        @overrides
        def name(self):
            return 'Git'

        @property
        def tools(self) -> Tools:
            """
            :return: Tools this uses to do its task.
            """
            return self._tools

        @overrides
        def jobs(self, spec: GitSpec) -> Iterable[Job]:
            LOG.debug("Preparing spec: '%s'...", spec)

            repo = self.tools.repositories.from_remote(url=spec.remote)
            directory = repo.workspace.cd(spec.directory)

            LOG.debug("Spec ready, parsing contents...")

            result = []

            for file in self.tools.files.search(directory):
                LOG.debug("Reading: '%s'...", file.file)
                reader = self.tools.readers.from_file(file)
                result += reader.jobs()

            return result

    def __init__(self):
        """Constructor.
        """
        super().__init__(get=GitBackend.Get())

    @property
    @overrides
    def get(self) -> Get:
        return super().get()
