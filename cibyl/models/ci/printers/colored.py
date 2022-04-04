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

from cibyl.models.ci.printers import Printer
from cibyl.utils.colors import Colors


class ColorProvider(ABC):
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


class ColoredText(ColorProvider):
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


class ColoredPrinter(Printer):
    def __init__(self, verbosity=0, color=ColoredText()):
        super().__init__(verbosity)

        self._color = color

    def print_environment(self, env):
        pass

    def print_jobs_system(self, system):
        pass

    def print_job(self, job):
        pass
