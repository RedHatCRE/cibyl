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
from enum import Enum


class OutputStyle(Enum):
    """Lists all supported output formats by the CLI.
    """
    TEXT = 0
    """A human-readable text based format."""
    COLORIZED = 1
    """Same as :attr:`TEXT` but colored for easier read."""
    JSON = 2
    """A machine-readable text based format."""

    @staticmethod
    def from_key(key: str) -> 'OutputStyle':
        """Parses a key into an :class:`OutputStyle`.

        Map of known keys:
            * 'text' -> OutputStyle.TEXT
            * 'colorized' -> OutputStyle.COLORIZED
            * 'json' -> OutputStyle.JSON

        :param key: The key to get the style for.
        :return: The correspondent style.
        :raise NotImplementedError: If no style is present for the
        given key.
        """
        if key == 'text':
            return OutputStyle.TEXT
        elif key == 'colorized':
            return OutputStyle.COLORIZED
        elif key == 'json':
            return OutputStyle.JSON
        else:
            raise NotImplementedError(f'Unknown format: {key}')
