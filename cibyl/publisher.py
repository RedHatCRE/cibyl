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
from abc import ABC
from enum import Enum

from cibyl.models.ci.printers import CIPrinterFactory

LOG = logging.getLogger(__name__)


class PrintMode(Enum):
    SIMPLE = 0
    COMPLETE = 1


class Printer(ABC):
    def __init__(self, mode=PrintMode.COMPLETE, verbosity=0):
        self._mode = mode
        self._verbosity = verbosity

    @property
    def mode(self):
        return self._mode

    @property
    def verbosity(self):
        return self._verbosity


class Publisher:
    """Represents a publisher which is responsible for publishing the data
    collected by the application in the chosen format and to the chosen
    location
    """

    @staticmethod
    def publish(
        environments, output_style,
        dest="terminal", verbosity=0, user_arguments=0
    ):
        """Publishes the data of the given environments to the
        chosen destination.
        """
        print_mode = PrintMode.COMPLETE

        # if the user did not pass any query argument (--jobs, --builds, ...)
        # print only a simple representation of the environment
        if user_arguments == 0:
            print_mode = PrintMode.SIMPLE

        if dest == "terminal":
            for env in environments:
                printer = CIPrinterFactory.from_style(
                    output_style, print_mode, verbosity
                )

                print(printer.print_environment(env))
