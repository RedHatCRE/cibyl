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
from typing import Iterable

LOG = logging.getLogger(__name__)


def _is_file_available(filename):
    """
    Checks if a file is available by trying to open to it.

    Args:
        filename(str): A path pointing to the file to be checked.
    Returns:
        (bool): Whether the file can be opened or not.
    """
    try:
        with open(filename, 'r'):
            return True
    except OSError:
        return False


def get_first_available_file(filenames, file_check=_is_file_available):
    """
    Searches for the first file out of the provided paths that exists on the
    host's drive.

    Args:
        filenames(Iterable[bytes | str | PathLike]): A list of paths pointing
            to different files.
        file_check: A function that determines if a file is present.
    Returns:
        str | None: A string containing the path to the found file. 'None'
            if no file is available.
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
