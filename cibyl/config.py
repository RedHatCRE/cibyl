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
import os
from collections import UserDict

import rfc3987

from cibyl.exceptions.cli import AbortedByUserError
from cibyl.exceptions.config import ConfigurationNotFound
from cibyl.utils import yaml
from cibyl.utils.files import get_first_available_file, is_file_available
from cibyl.utils.net import DownloadError, download_file

LOG = logging.getLogger(__name__)


class Config(UserDict):
    """Representation of a Cybil's configuration file. Even though it starts
    without any contents, this dictionary can be filled in with the data
    from an external yaml file. No post-processing is performed on the read
    data, as this class acts as a direct interface between the system's file
    and the app.
    """

    def load(self, file):
        """Loads the contents of a file into this object. Any contents this
        may beforehand have are lost and replaced by the data from the file.
        In case of error, the contents are left untouched.

        :raises YAMLError: If the file could not be parsed.
        """
        self.data = yaml.parse(file)


class ConfigFactory:
    """Factory that generates already loaded configurations from different
    sources.
    """

    DEFAULT_USER_PATH = os.path.join(
        os.path.expanduser('~'), '.config/cibyl.yaml'
    )
    """Default location on the user's filesystem where the configuration
    file is expected.
    """

    DEFAULT_FILE_PATHS = (
        DEFAULT_USER_PATH,
        '/etc/cibyl/cibyl.yaml'
    )
    """List of locations where the configuration should be by defaults.
    Ordered from user scope to system scope.
    """

    @staticmethod
    def from_path(path):
        """Build a configuration from a random path. This path may be a URL,
        a file path or any other. If the path is 'None', then this will look
        for the first definition available among the default paths.

        :param path: The path to get the definition from.
        :type path: str or None
        :return: The configuration instance.
        :rtype: :class:`Config`
        :raise ConfigurationNotFound: If no definition could be
            retrieved.
        """
        if not path:
            return ConfigFactory.from_search()

        if rfc3987.match(path, 'URI'):
            return ConfigFactory.from_url(path)

        return ConfigFactory.from_file(path)

    @staticmethod
    def from_file(file):
        """Builds a configuration from a file located on the local filesystem.

        :param file: Path to the configuration definition.
        :type file: str
        :return: The configuration instance
        :rtype: :class:`Config`
        :raise ConfigurationNotFound: If the file does not exist.
        """
        if not is_file_available(file):
            raise ConfigurationNotFound(f'No file at: {file}')

        config = Config()
        config.load(file)

        return config

    @staticmethod
    def from_search():
        """Builds a configuration from the first available definition found
        between the default paths.

        :return: The configuration instance
        :rtype: :class:`Config`
        :raise ConfigurationNotFound: If no definition could be found.
        """
        paths = ConfigFactory.DEFAULT_FILE_PATHS
        file = get_first_available_file(paths)

        if not file:
            msg = f'Could not find configuration file at: {paths}'

            raise ConfigurationNotFound(msg)

        return ConfigFactory.from_file(file)

    @staticmethod
    def from_url(url, dest=DEFAULT_USER_PATH):
        """Builds a configuration from a definition located on a remote
        host. The definition is accessed and downloaded into the provided path.

        Supported protocols are defined by
        :func:`cibyl.utils.net.download_file`.

        Warnings
        -------
        In case that a file already exists at the destination, this will ask
        the user whether they want to overwrite it or not. This requires
        interaction with the CLI and can block callers.

        Examples
        --------
        >>> ConfigFactory.from_url(
                'http://localhost/my-file.yaml', '/var/cibyl/config.yaml'
            )

        :param url: The URL where the file is located at.
        :type url: str
        :param dest: Path where the definition will be downloaded
            into. Must contain name of the file.
        :type dest: str
        :return: The configuration instance
        :rtype: :class:`Config`
        :raise ConfigurationNotFound: If the definition could not
            be downloaded.
        """
        LOG.info("Trying to obtain configuration file from: %s", url)

        # Is there something on the download path?
        if is_file_available(dest):
            # Ask user if they want to overwrite it then
            user_answer = ''

            while user_answer not in ('y', 'n'):
                print(f'Configuration file already found at: {dest}')
                print('Overwrite file? [y/n](n):')
                user_answer = input()

                if not user_answer:
                    user_answer = 'n'

            if user_answer == 'n':
                raise AbortedByUserError

            if user_answer == 'y':
                LOG.info('Deleting file at: %s', dest)
                os.remove(dest)

        # Download the file
        LOG.info("Downloading file into: %s", dest)

        try:
            download_file(url, dest)
        except DownloadError as ex:
            msg = f'Configuration could not be retrieved from: {url}'

            raise ConfigurationNotFound(msg) from ex

        LOG.info('Download completed successfully.')

        return ConfigFactory.from_file(dest)
