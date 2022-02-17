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
import sys
import os
import yaml

from cibyl.files import get_first_available_file
from collections import UserDict

LOG = logging.getLogger(__name__)


class Config(UserDict):
    """
    """
    DEFAULT_FILE_PATHS = (
        os.path.join(os.path.expanduser('~'), '.cibyl/cibyl.yaml'),
        '/etc/cibyl/cibyl.yaml'
    )

    def load(self, path):
        """
        :return:
        """
        try:
            with open(path, 'r') as file:
                self.data = yaml.safe_load(file)

        except OSError:
            LOG.error('{}: {}'.format('unable to load file at', path))
            sys.exit(2)

    @staticmethod
    def get_config_file_path(arguments, system_paths=DEFAULT_FILE_PATHS):
        """
        Manually parse user arguments and check if config
        argument was used. If yes, use the value provided.
        If not, search the host for places where the file
        may be.

        Args:
            arguments: List of arguments.
            system_paths: List of locations on the host where the
            configuration files may be located. The class defines a set of
            common locations that it uses by default.
        Returns:
            A string which is the config file path. 'None' if the config file
            could not be located.
        """
        for i, item in enumerate(arguments[1:]):
            if item == '--config':
                return arguments[i + 2]

        return get_first_available_file(system_paths)
