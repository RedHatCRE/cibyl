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

from tripleo.insights.git import GitCLIDownloader, GitDownloaderFetcher
from tripleo.utils.urls import URL


class TestGitDownloaderFetcher(TestCase):
    """Tests for :class:`GitDownloaderFetcher`.
    """

    def test_different_working_directory_per_instance(self):
        """Checks that different instances of the fetcher do not reuse the
        same working directory for CLI downloaders.
        """
        url = URL('http://localhost:8080/my_repo.git')

        fetcher1 = GitDownloaderFetcher()
        fetcher2 = GitDownloaderFetcher()

        downloaders1 = fetcher1.get_downloaders_for(url)
        downloaders2 = fetcher2.get_downloaders_for(url)

        self.assertEqual(1, len(downloaders1))
        self.assertEqual(1, len(downloaders2))

        cli1 = downloaders1[0]
        cli2 = downloaders2[0]

        self.assertIsInstance(cli1, GitCLIDownloader)
        self.assertIsInstance(cli2, GitCLIDownloader)

        self.assertNotEqual(cli2.working_dir, cli1.working_dir)

    def test_reuses_working_directory(self):
        """Checks that instead of telling the CLI downloader to clone into a
        new working directory each time, the fetcher will reuse one assigned
        to it during creation.

        This will save time, space and network problems. The downloader will
        get to open the already cloned repository instead of cloning it again.
        """
        url = URL('http://localhost:8080/my_repo.git')

        fetcher1 = GitDownloaderFetcher()

        downloaders1 = fetcher1.get_downloaders_for(url)
        downloaders2 = fetcher1.get_downloaders_for(url)

        self.assertEqual(1, len(downloaders1))
        self.assertEqual(1, len(downloaders2))

        cli1 = downloaders1[0]
        cli2 = downloaders2[0]

        self.assertIsInstance(cli1, GitCLIDownloader)
        self.assertIsInstance(cli2, GitCLIDownloader)

        self.assertEqual(cli2.working_dir, cli1.working_dir)
