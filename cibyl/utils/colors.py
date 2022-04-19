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
    def red(text):
        return f"{Colors.RED}{Colors.BOLD}{text}{Colors.CLOSE}"

    @staticmethod
    def green(text):
        return f"{Colors.GREEN}{Colors.BOLD}{text}{Colors.CLOSE}"

    @staticmethod
    def blue(text):
        return f"{Colors.BLUE}{Colors.BOLD}{text}{Colors.CLOSE}"

    @staticmethod
    def yellow(text):
        return f"{Colors.YELLOW}{text}{Colors.CLOSE}"

    @staticmethod
    def underline(text):
        return f"{Colors.UNDERLINE}{text}{Colors.CLOSE}"


class ColorPalette(ABC):
    @abstractmethod
    def red(self, text):
        raise NotImplementedError

    @abstractmethod
    def green(self, text):
        raise NotImplementedError

    @abstractmethod
    def blue(self, text):
        raise NotImplementedError

    @abstractmethod
    def yellow(self, text):
        raise NotImplementedError

    @abstractmethod
    def underline(self, text):
        raise NotImplementedError


class DefaultPalette(ColorPalette):
    def red(self, text):
        return Colors.red(text)

    def green(self, text):
        return Colors.green(text)

    def blue(self, text):
        return Colors.blue(text)

    def yellow(self, text):
        return Colors.yellow(text)

    def underline(self, text):
        return Colors.underline(text)


class ClearText(ColorPalette):
    def red(self, text):
        return text

    def green(self, text):
        return text

    def blue(self, text):
        return text

    def yellow(self, text):
        return text

    def underline(self, text):
        return text
