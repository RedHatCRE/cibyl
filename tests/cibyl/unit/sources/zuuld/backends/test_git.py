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
from unittest import TestCase
from unittest.mock import Mock

from cibyl.sources.zuuld.backends.git import GitBackend


class TestGitBackend(TestCase):
    """Tests for :class:`GitBackend`.
    """

    def test_reads_jobs(self):
        spec = Mock()
        spec.remote = Mock()
        spec.directory = Mock()

        directory = Mock()
        expected = [Mock(), Mock()]

        repo = Mock()
        repo.workspace = Mock()
        repo.workspace.cd = Mock()
        repo.workspace.cd.return_value = directory

        repositories = Mock()
        repositories.from_remote = Mock()
        repositories.from_remote.return_value = repo

        files = Mock()
        files.search = Mock()
        files.search.return_value = [Mock()]

        reader = Mock()
        reader.jobs = Mock()
        reader.jobs.return_value = expected

        readers = Mock()
        readers.from_file = Mock()
        readers.from_file.return_value = reader

        tools = Mock()
        tools.repositories = repositories
        tools.files = files
        tools.readers = readers

        git = GitBackend.Get(
            tools=tools
        )

        result = git.jobs(spec)

        self.assertEqual(expected, result)

        repositories.from_remote.assert_called_with(url=spec.remote)
        repo.workspace.cd.assert_called_with(spec.directory)

        files.search.assert_called_with(directory)
        readers.from_file.assert_called_with(files.search.return_value[0])

        reader.jobs.assert_called()
