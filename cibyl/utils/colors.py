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
from abc import ABC, abstractmethod


class Colors:
    """This is an implementation of a color class"""

    BLUE = '\033[94m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CLOSE = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @staticmethod
    def red(text: str) -> str:
        return f"{Colors.RED}{Colors.BOLD}{text}{Colors.CLOSE}"

    @staticmethod
    def green(text: str) -> str:
        return f"{Colors.GREEN}{Colors.BOLD}{text}{Colors.CLOSE}"

    @staticmethod
    def blue(text: str) -> str:
        return f"{Colors.BLUE}{Colors.BOLD}{text}{Colors.CLOSE}"

    @staticmethod
    def yellow(text: str) -> str:
        return f"{Colors.YELLOW}{text}{Colors.CLOSE}"

    @staticmethod
    def bold(text: str) -> str:
        return f"{Colors.BOLD}{text}{Colors.CLOSE}"

    @staticmethod
    def underline(text: str) -> str:
        return f"{Colors.UNDERLINE}{text}{Colors.CLOSE}"


class ColorPalette(ABC):
    """Represents the palette of colors used on output.
    """

    @abstractmethod
    def red(self, text):
        """Paints text with the color red.

        :param text: The text to paint.
        :return: The painted text.
        :rtype: str
        """
        raise NotImplementedError

    @abstractmethod
    def green(self, text):
        """Paints text with the color green.

        :param text: The text to paint.
        :return: The painted text.
        :rtype: str
        """
        raise NotImplementedError

    @abstractmethod
    def blue(self, text):
        """Paints text with the color blue.

        :param text: The text to paint.
        :return: The painted text.
        :rtype: str
        """
        raise NotImplementedError

    @abstractmethod
    def yellow(self, text):
        """Paints text with the color yellow.

        :param text: The text to paint.
        :return: The painted text.
        :rtype: str
        """
        raise NotImplementedError

    @abstractmethod
    def bold(self, text):
        """Bolds text.

        :param text: The text to paint.
        :return: The painted text.
        :rtype: str
        """
        raise NotImplementedError

    @abstractmethod
    def underline(self, text):
        """Underlines text.

        :param text: The text to underline.
        :return: The underlined text.
        :rtype: str
        """
        raise NotImplementedError


class DefaultPalette(ColorPalette):
    """The default color scheme of the app.
    """

    def red(self, text: str) -> str:
        return Colors.red(text)

    def green(self, text: str) -> str:
        return Colors.green(text)

    def blue(self, text: str) -> str:
        return Colors.blue(text)

    def yellow(self, text: str) -> str:
        return Colors.yellow(text)

    def bold(self, text: str) -> str:
        return Colors.bold(text)

    def underline(self, text: str) -> str:
        return Colors.underline(text)


class ClearText(ColorPalette):
    """A palette without colors. Leaves all text as is. Used to disable
    coloring wherever it is present.
    """

    def red(self, text: str) -> str:
        return text

    def green(self, text: str) -> str:
        return text

    def blue(self, text: str) -> str:
        return text

    def yellow(self, text: str) -> str:
        return text

    def bold(self, text: str) -> str:
        return text

    def underline(self, text: str) -> str:
        return text
