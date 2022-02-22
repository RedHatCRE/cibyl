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
from typing import Iterable
import logging
import os
from collections import UserDict

from cibyl.files import get_first_available_file
import cibyl.yaml as yaml

LOG = logging.getLogger(__name__)


class Config(UserDict):
    """
    Representation of a Cybil's configuration file. Even though it starts
    without any contents, this dictionary can be filled in with the data
    of an external yaml file. No post-processing is performed on the read
    data, as this class acts as a direct interface between the system's file
    and the app.
    """

    DEFAULT_FILE_PATHS = (
        os.path.join(os.path.expanduser('~'), '.cibyl/cibyl.yaml'),
        '/etc/cibyl/cibyl.yaml'
    )
    """
    Collection of paths where the configuration file for the app is
    expected to be found by default.
    """

    def load(self, path=DEFAULT_FILE_PATHS):
        """
        Loads the contents of a configuration file into this object.

        Args:
            path(str | Iterable[str]): Path to the configuration file to be
                read. If more than one path is provided, this will load the
                first file than it finds available, following the iteration
                order indicated by the container.
        Raises:
            FileNotFoundError: If file at provided path was not found.
            YAMLError: If the configuration file could not be parsed.
        """
        if isinstance(path, str):
            path = [path]

        if file := get_first_available_file(path):
            self.data = yaml.parse(file)
        else:
            raise FileNotFoundError(f"Could not open file at: '{path}'")
