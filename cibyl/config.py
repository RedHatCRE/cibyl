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
from typing import Callable, Optional

import rfc3987
from jsonschema.exceptions import ValidationError

import cibyl.exceptions.config as conf_exc
from cibyl import __path__ as pwd
from cibyl.cli.interactions import ask_yes_no_question
from cibyl.exceptions.cli import AbortedByUserError
from cibyl.exceptions.config import SchemaError
from cibyl.models.ci.system_factory import SystemType
from cibyl.utils import yaml
from cibyl.utils.files import get_first_available_file, is_file_available
from cibyl.utils.fs import File, cd_context_manager
from cibyl.utils.json import Draft7ValidatorFactory
from cibyl.utils.net import DownloadError, download_file

LOG = logging.getLogger(__name__)


def _ask_user_for_overwrite() -> bool:
    """Prints a question on the command line asking whether the user would
    like to continue with a file overwrite or not.

    ..  warning::
            Blocking call, requires interaction.

    :return: True if the user answered yes, false if not.
    """
    return ask_yes_no_question('Overwrite file?')


class Config(UserDict):
    """Representation of a generic configuration file. Even though it starts
    without any contents, this dictionary can be filled in with the data
    from an external yaml file. No post-processing is performed on the read
    data, as this class acts as a direct interface between the system's file
    and the app.
    """

    def load_from_path(self, path: str) -> None:
        """Loads the content of a configuration file/object and creates
        a reference to environments."""
        if path:
            self.data = ConfigFactory.from_path(path)
        else:
            self.data = ConfigFactory.from_search()


class AppConfig(Config):
    """Representation of a Cybil's configuration file"""

    def __init__(
        self,
        data: Optional[dict] = None,
        schema: File = File('_data/schemas/config.json')
    ):
        super().__init__(data)

        self._schema = schema

    @property
    def environments(self) -> dict:
        """dict: environments section from the configuration data."""
        return self.data.get('environments', {})

    @property
    def plugins(self) -> list:
        """dict: plugins section from the configuration data."""
        return self.data.get('plugins', [])

    def load(self, path: str = None) -> None:
        """Loads the content of a configuration file/object and creates
        a reference to environments.

        :param path: The path of a configuration file
        :type path: str
        :raise ConfigurationNotFound: If no definition could be retrieved.
        :raise EmptyConfiguration: If configuration file is empty.
        """
        super().load_from_path(path)

    def verify(self) -> None:
        """Verifies the configuration content by the context of the
        application (using concepts like environments, systems and sources.

        :raise MissingSystems: If a specific environment section is empty
        :raise MissingEnvironments: If no environments specified
        """
        self._verify_by_hand()
        self._verify_by_schema()

    def _verify_by_hand(self) -> None:
        self._verify_environments()
        self._verify_systems()

    def _verify_environments(self) -> None:
        """Checks whether the environments section in the configuration
        is valid.

        :raise MissingSystems: If a specific environment section is empty
        :raise MissingEnvironments: If no environments specified
        """
        if isinstance(self.environments, str):
            raise conf_exc.MissingSystems(self.environments)
        if not self.environments:
            raise conf_exc.MissingEnvironments()

    def _verify_systems(self) -> None:
        """Checks whether the systems of each environment
        in the configuration are properly defined.

        :raise MissingSystemType: If the type of a system is missing
        :raise MissingSystems: If no systems specified for an environment
        """
        for env_name, systems_dict in self.environments.items():
            if isinstance(systems_dict, str):
                raise conf_exc.MissingSystemType(systems_dict, SystemType)
            try:
                systems_dict.get('foo', None)
            except AttributeError:
                raise conf_exc.MissingSystems(env_name)
            for system_name, single_system in systems_dict.items():
                if isinstance(single_system, dict):
                    self._verify_sources(system_name, single_system)

    def _verify_sources(self, system_name: str, system_data: dict) -> None:
        """Checks whether a given system includes definition of sources.

        :param system_name: The name of a given system
        :param system_data: The configuration dict of a system
        :raise MissingSystemSources: If sources are not defined for a system
        """
        if 'sources' not in system_data:
            raise conf_exc.MissingSystemSources(system_name)

    def _verify_by_schema(self):
        with cd_context_manager(pwd[0]):
            validators = Draft7ValidatorFactory()
            validator = validators.from_file(self._schema)

            try:
                validator.validate(self.data)
            except ValidationError as ex:
                raise SchemaError(error=ex.message)


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
    def from_path(path: str) -> dict:
        """Build a configuration from a random path. This path may be a URL,
        a file path or any other. If the path is 'None', then this will look
        for the first definition available among the default paths.

        :param path: The path to get the definition from.
        :return: The configuration instance.
        :raise ConfigurationNotFound: If no definition could be retrieved.
        :raise EmptyConfiguration: If configuration file is empty.
        """
        if not path:
            return ConfigFactory.from_search()

        if rfc3987.match(path, 'URI'):
            return ConfigFactory.from_url(path)

        return ConfigFactory.from_file(path)

    @staticmethod
    def from_file(file: str) -> dict:
        """Builds a configuration from a file located on the local filesystem.

        :param file: Path to the configuration definition.
        :return: The configuration instance
        :raise ConfigurationNotFound: If the file does not exist.
        """
        if not is_file_available(file):
            raise conf_exc.ConfigurationNotFound(file)
        data = yaml.parse(file)
        if data is None:
            # if the configuration file is empty, yaml.parse will return None,
            # we assign an empty dictionary to always return the same type and
            # raise an exception
            data = {}
            raise conf_exc.EmptyConfiguration(file)
        return data

    @staticmethod
    def from_search() -> dict:
        """Builds a configuration from the first available definition found
        between the default paths.

        :return: The configuration instance
        :raise ConfigurationNotFound: If no definition could be found.
        """
        paths = ConfigFactory.DEFAULT_FILE_PATHS
        file = get_first_available_file(paths)

        if not file:
            raise conf_exc.ConfigurationNotFound(paths)

        return ConfigFactory.from_file(file)

    @staticmethod
    def from_url(
        url: str, dest: str = DEFAULT_USER_PATH,
        overwrite_call: Callable[[], bool] = _ask_user_for_overwrite
    ) -> dict:
        """Builds a configuration from a definition located on a remote
        host. The definition is accessed and downloaded into the provided path.

        Supported protocols are defined by
        :func:`cibyl.utils.net.download_file`.

        Warnings
        -------
        In case a file already exists at the destination, this will ask by
        default if the user wants to overwrite it or not. This requires
        interaction with the CLI and therefore is a blocker.

        Examples
        --------
        >>> ConfigFactory.from_url(
                'http://localhost/my-file.yaml', '/var/cibyl/config.yaml'
            )

        :param url: The URL where the file is located at.
        :param dest: Path where the definition will be downloaded
            into. Must contain name of the file.
        :param overwrite_call: The function used to ask the user if they
            may overwrite the file. Change to avoid blocker.
        :return: The configuration instance
        :raise ConfigurationNotFound: If the definition could not
            be downloaded.
        """
        LOG.info("Trying to obtain configuration file from: %s", url)

        # Is there something on the download path?
        if is_file_available(dest):
            # Overwrite it then?
            print(f'Configuration file already found at: {dest}')

            if overwrite_call():
                LOG.info('Deleting file at: %s', dest)
                os.remove(dest)
            else:
                raise AbortedByUserError

        # Download the file
        LOG.info("Downloading file into: %s", dest)

        try:
            download_file(url, dest)
        except DownloadError as ex:
            raise conf_exc.ConfigurationNotFound(url) from ex

        LOG.info('Download completed successfully.')

        return ConfigFactory.from_file(dest)
