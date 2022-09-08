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
from enum import Enum

LOG = logging.getLogger(__name__)


class OutputArrangement(Enum):
    """Lists all supported dispositions models can be presented in for a plain
    text style.
    """
    LIST = 0
    """Show models as individual collections of elements.

    For example:
        - Jobs:
            - A
            - B
            - C
        - Builds:
            - Job: A
                - 1
                - 2
                - 3
    """
    HIERARCHY = 1
    """Show models following the hierarchy they follow at their host.

    For example:
        - Jobs:
            - A
              Builds:
                - 1
                - 2
                - 3
    """

    @staticmethod
    def from_kwargs(**kwargs) -> 'OutputArrangement':
        """Looks for the 'arrangement' key and returns the correct option for
        its value.

        In case the key in not present, then the 'list' option is returned.
        In case the key points to an unknown value, then the 'list' option
        is also returned.

        List of known values:
            - 'list'
            - 'hierarchy'

        :param kwargs: Arguments to look for the key in.
        :return: The chosen option.
        """
        arrangement = kwargs.get('arrangement')

        if not arrangement:
            msg = "'arrangement' key not found. Defaulting to list mode..."
            LOG.debug(msg)
            return OutputArrangement.LIST

        if arrangement == 'list':
            return OutputArrangement.LIST

        if arrangement == 'hierarchy':
            return OutputArrangement.HIERARCHY

        msg = "Unknown arrangement: '%s'. Defaulting to list mode..."
        LOG.debug(msg, arrangement)
        return OutputArrangement.LIST


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
