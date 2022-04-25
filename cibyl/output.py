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
from abc import ABC
from enum import Enum


class PrintMode(Enum):
    """Defines the multiple ways on which a model can be printed within an
    output style.
    """
    SIMPLE = 0
    """Prints the minimum amount of information on a model for it to be
    distinguishable."""
    COMPLETE = 1
    """Prints all the information contained on a model."""


class Printer(ABC):
    """Base class for all implementations of an output style.
    """

    def __init__(self, mode=PrintMode.COMPLETE, verbosity=0):
        """Constructor.

        :param mode: Amount of information desired on the printed result.
        :type mode: :class:`PrintMode`
        :param verbosity: How verbose the output is to be expected.
            The higher this value is, the more text will be printed.
            This differs from the mode in that the mode selects the data to be
            printed while this how much is to be said about each entry.
        :type verbosity: int
        """
        self._mode = mode
        self._verbosity = verbosity

    @property
    def mode(self):
        """
        :return: The print mode of this printer.
        :rtype: :class:`PrintMode`
        """
        return self._mode

    @property
    def verbosity(self):
        """
        :return: Verbosity level of this printer.
        :rtype: int
        """
        return self._verbosity
