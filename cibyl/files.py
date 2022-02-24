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
from os import PathLike

LOG = logging.getLogger(__name__)


def _is_file_available(filename):
    """Checks if a file is present on the filesystem.

    :param filename: A path pointing to the file to be checked.
    :type filename: str
    :return: Whether the file is there or not.
    :rtype: bool
    """
    return os.path.isfile(filename)


def get_first_available_file(filenames, file_check=_is_file_available):
    """Searches for the first file out of the provided paths that exists
    on the host's drive.

    :param filenames: A list of paths pointing to different files.
    :type filenames: :class:`typing.Iterable[bytes | str | PathLike]`
    :param file_check: A function that determines if a file is present.
    :return: A string containing the path to the found file. 'None' if no
        file is available
    :rtype: bytes or str or None
    """
    for filename in filenames:
        # Resolve path into a string
        if isinstance(filename, PathLike):
            filename = os.fspath(filename)

        # Check if file exists
        if file_check(filename):
            return filename

        LOG.debug('%s: %s', 'file not found', filename)

    # None of the files exist
    return None
