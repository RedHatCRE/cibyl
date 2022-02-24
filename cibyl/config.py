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

from cibyl.utils import yaml
from cibyl.utils.files import get_first_available_file

LOG = logging.getLogger(__name__)


class Config(UserDict):
    """Representation of a Cybil's configuration file. Even though it starts
    without any contents, this dictionary can be filled in with the data
    from an external yaml file. No post-processing is performed on the read
    data, as this class acts as a direct interface between the system's file
    and the app.

    :ivar _path: Path, or collection of paths, to the configuration file
        this represents.
    """

    DEFAULT_FILE_PATHS = (
        os.path.join(os.path.expanduser('~'), '.cibyl/cibyl.yaml'),
        '/etc/cibyl/cibyl.yaml'
    )
    """Collection of paths where the configuration file for the app is
    expected to be found by default.
    """

    def __init__(self, path=None):
        """Constructor.

        :param path: Paths to the configuration file to be read. If 'None' is
            provided, this will search for the file in a collection of well
            known paths.
        :type path: None or str or :class:`typing.Iterable[str]`
        """
        super().__init__()

        self._path = path

    @property
    def path(self):
        """Getter for the paths where this searches through.

        :return: A list of paths.
        :rtype: :class:`typing.Iterable[str]`
        """
        if not self._path:
            # User provided nothing, use default paths then
            return self.DEFAULT_FILE_PATHS

        # Returned value must be a list
        if isinstance(self._path, str):
            return [self._path]

        return self._path

    def load(self):
        """Loads the contents of the configuration file into this object.
        This will look for the first file available from the list of paths
        provided by :attr:`~path`.

        :raises FileNotFoundError: If no configuration file could be found.
        :raises YAMLError: If the configuration file could not be parsed.
        """
        if file := get_first_available_file(self.path):
            self.data = yaml.parse(file)
        else:
            raise FileNotFoundError(f"Could not open file at: '{self.path}'")
