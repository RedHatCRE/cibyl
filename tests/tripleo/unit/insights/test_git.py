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
from unittest.mock import Mock, call, patch

from tripleo.insights.exceptions import DownloadError
from tripleo.insights.git import (GitCLIDownloader, GitDownload,
                                  GitDownloaderFetcher, GitHubDownloader)
from tripleo.utils.yaml import YAMLError


class TestGitCLIDownloader(TestCase):
    """Tests for :class:`GitCLIDownloader`.
    """

    def test_downloads_file_from_new_repo(self):
        """Checks that the downloader takes the steps to get the contents
        of a file when the repository has never been cloned.
        """
        contents = 'contents_of_file'

        url = Mock()
        file = Mock()
        branch = Mock()

        working_dir = Mock()
        working_dir.is_empty = Mock()
        working_dir.is_empty.return_value = True

        repo = Mock()
        repo.checkout = Mock()
        repo.get_as_text = Mock()
        repo.get_as_text.return_value = contents

        api = Mock()
        api.clone = Mock()
        api.clone.return_value = repo

        downloader = GitCLIDownloader(
            repository=url,
            working_dir=working_dir,
            branch=branch,
            api=api
        )

        result = downloader.download_as_text(file)

        self.assertEqual(contents, result)

        working_dir.is_empty.assert_called_once()

        api.clone.assert_called_once_with(url, working_dir)

        repo.checkout.assert_called_once_with(branch)
        repo.get_as_text.assert_called_once_with(file)

    def test_downloads_file_from_old_repo(self):
        """Checks that the downloader takes the steps to get the contents
        of a file when the repository is already cloned.
        """
        contents = 'contents_of_file'

        url = Mock()
        file = Mock()
        branch = Mock()

        working_dir = Mock()
        working_dir.is_empty = Mock()
        working_dir.is_empty.return_value = False

        remote = Mock()
        remote.urls = [url]

        repo = Mock()
        repo.remotes = [remote]
        repo.checkout = Mock()
        repo.get_as_text = Mock()
        repo.get_as_text.return_value = contents

        api = Mock()
        api.open = Mock()
        api.open.return_value = repo

        downloader = GitCLIDownloader(
            repository=url,
            working_dir=working_dir,
            branch=branch,
            api=api
        )

        result = downloader.download_as_text(file)

        self.assertEqual(contents, result)

        working_dir.is_empty.assert_called_once()

        api.open.assert_called_once_with(working_dir)

        repo.checkout.assert_called_once_with(branch)
        repo.get_as_text.assert_called_once_with(file)


class TestGitHubDownloader(TestCase):
    """Tests for :class:`GitHubDownloader`.
    """

    @patch('tripleo.insights.git.get_repository_fullname')
    def test_downloads_as_text(self, fullname_mock: Mock):
        """Checks that the necessary steps are taken to download a file as
        text from GitHub.
        """
        contents = 'contents_of_file'

        url = Mock()
        file = Mock()
        branch = Mock()

        fullname_mock.return_value = 'owner/repo'

        repo = Mock()
        repo.checkout = Mock()
        repo.download_as_text = Mock()
        repo.download_as_text.return_value = contents

        api = Mock()
        api.get_repository = Mock()
        api.get_repository.return_value = repo

        downloader = GitHubDownloader(
            repository=url,
            branch=branch,
            api=api
        )

        result = downloader.download_as_text(file)

        self.assertEqual(contents, result)

        fullname_mock.assert_has_calls([call(url), call(url)])

        api.get_repository.assert_called_once_with('owner', 'repo')

        repo.checkout.assert_called_once_with(branch)
        repo.download_as_text.assert_called_once_with(file)


class TestGitDownloaderFetcher(TestCase):
    """Tests for :class:`GitDownloaderFetcher`.
    """

    @patch('tripleo.insights.git.is_git')
    def test_get_downloaders_for_unknown(self, git_check: Mock):
        """Checks the found downloaders for an unknown URL.
        """
        url = Mock()
        branch = Mock()

        git_check.return_value = False

        fetcher = GitDownloaderFetcher()

        result = fetcher.get_downloaders_for(url, branch)

        self.assertEqual(0, len(result))

        git_check.assert_called_once_with(url)

    @patch('tripleo.insights.git.is_github')
    @patch('tripleo.insights.git.is_git')
    def test_get_downloaders_for_git(
        self,
        git_check: Mock,
        github_check: Mock
    ):
        """Checks the found downloaders for a generic Git URL.
        """
        url = Mock()
        branch = Mock()

        git_check.return_value = True
        github_check.return_value = False

        fetcher = GitDownloaderFetcher()

        result = fetcher.get_downloaders_for(url, branch)

        self.assertEqual(1, len(result))

        self.assertIsInstance(result[0], GitCLIDownloader)

        self.assertEqual(branch, result[0].branch)

        git_check.assert_called_once_with(url)
        github_check.assert_called_once_with(url)

    @patch('tripleo.insights.git.is_github')
    @patch('tripleo.insights.git.is_git')
    def test_get_downloaders_for_github(
        self,
        git_check: Mock,
        github_check: Mock
    ):
        """Checks the found downloaders for a GitHub URL.
        """
        url = Mock()
        branch = Mock()

        git_check.return_value = True
        github_check.return_value = True

        fetcher = GitDownloaderFetcher()

        result = fetcher.get_downloaders_for(url, branch)

        self.assertEqual(2, len(result))

        self.assertIsInstance(result[0], GitHubDownloader)
        self.assertIsInstance(result[1], GitCLIDownloader)

        self.assertEqual(branch, result[0].branch)
        self.assertEqual(branch, result[1].branch)

        git_check.assert_called_once_with(url)
        github_check.assert_called_once_with(url)


class TestGitDownload(TestCase):
    """Tests for :class:`GitDownload`.
    """

    def test_error_if_no_downloaders_on_downloads_as_yaml(self):
        """Checks that an error is raised if there are no downloaders
        for the given URL when downloading file as YAML."""

        repo = Mock()
        file = Mock()
        branch = Mock()

        fetcher = Mock()
        fetcher.get_downloaders_for = Mock()
        fetcher.get_downloaders_for.return_value = []

        download = GitDownload(
            downloader_fetcher=fetcher
        )

        with self.assertRaises(DownloadError):
            download.download_as_yaml(repo, file, branch)

        fetcher.get_downloaders_for.assert_called_once_with(repo, branch)

    def test_error_if_all_fail_on_downloads_as_yaml(self):
        """Checks that an error is thrown is all downloaders fail to
        download the file from the repo.
        """

        def raise_error(*_):
            raise DownloadError

        repo = Mock()
        file = Mock()
        branch = Mock()

        downloader = Mock()
        downloader.download_as_text = Mock()
        downloader.download_as_text.side_effect = raise_error

        fetcher = Mock()
        fetcher.get_downloaders_for = Mock()
        fetcher.get_downloaders_for.return_value = [downloader]

        download = GitDownload(
            downloader_fetcher=fetcher
        )

        with self.assertRaises(DownloadError):
            download.download_as_yaml(repo, file, branch)

    def test_error_if_not_yaml_on_downloads_as_yaml(self):
        """Checks that an error is raised if the contents of the downloaded
        file are not in YAML format.
        """

        def raise_error(*_):
            raise YAMLError

        repo = Mock()
        file = Mock()
        branch = Mock()

        contents = Mock()

        downloader = Mock()
        downloader.download_as_text = Mock()
        downloader.download_as_text.return_value = contents

        parser = Mock()
        parser.as_yaml = Mock()
        parser.as_yaml.side_effect = raise_error

        fetcher = Mock()
        fetcher.get_downloaders_for = Mock()
        fetcher.get_downloaders_for.return_value = [downloader]

        download = GitDownload(
            downloader_fetcher=fetcher
        )

        with self.assertRaises(DownloadError):
            download.download_as_yaml(repo, file, branch, yaml_parser=parser)

    def test_downloads_as_yaml(self):
        """Checks that it is possible to download a YAML file and parse.
        """
        repo = Mock()
        file = Mock()
        branch = Mock()

        contents = Mock()
        yaml = Mock()

        downloader = Mock()
        downloader.download_as_text = Mock()
        downloader.download_as_text.return_value = contents

        parser = Mock()
        parser.as_yaml = Mock()
        parser.as_yaml.return_value = yaml

        fetcher = Mock()
        fetcher.get_downloaders_for = Mock()
        fetcher.get_downloaders_for.return_value = [downloader]

        download = GitDownload(
            downloader_fetcher=fetcher
        )

        self.assertEqual(
            yaml,
            download.download_as_yaml(repo, file, branch, yaml_parser=parser)
        )

        downloader.download_as_text.assert_called_once_with(file)

        parser.as_yaml.assert_called_once_with(contents)
