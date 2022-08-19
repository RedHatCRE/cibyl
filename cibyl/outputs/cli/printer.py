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
from dataclasses import dataclass
from typing import Callable, NamedTuple

from cibyl.cli.query import QueryType
from cibyl.utils.colors import ColorPalette, DefaultPalette


class Printer(ABC):
    """Base class for all implementations of an output style.
    """

    def __init__(self,
                 query: QueryType = QueryType.NONE,
                 verbosity: int = 0):
        """Constructor.

        :param query: Type of query requested by the user. Determines how
            far down the model hierarchy the printer will go.
        :param verbosity: How verbose the output is to be expected. The
            bigger this is, the more is printed for each hierarchy level.
        """
        self._query = query
        self._verbosity = verbosity

    @property
    def query(self) -> QueryType:
        """
        :return: Query type requested by user.
        """
        return self._query

    @property
    def verbosity(self):
        """
        :return: Verbosity level of this printer.
        :rtype: int
        """
        return self._verbosity


class ColoredPrinter(Printer, ABC):
    """Base class for output styles based around coloring.
    """

    class Config(NamedTuple):
        query: QueryType
        palette: ColorPalette
        verbosity: int

    def __init__(self,
                 query: QueryType = QueryType.NONE,
                 verbosity: int = 0,
                 palette: ColorPalette = DefaultPalette()):
        """Constructor.

        See parents for more information.

        :param palette: Palette of colors to be used.
        """
        super().__init__(query, verbosity)

        self._palette = palette

    @property
    def config(self) -> Config:
        return ColoredPrinter.Config(
            query=self.query,
            palette=self.palette,
            verbosity=self.verbosity
        )

    @property
    def palette(self) -> ColorPalette:
        """
        :return: The palette currently in use.
        """
        return self._palette


class SerializedPrinter(Printer, ABC):
    @dataclass
    class Config:
        query: QueryType
        verbosity: int

    def __init__(self,
                 load_function: Callable[[str], dict],
                 dump_function: Callable[[dict], str],
                 query: QueryType = QueryType.NONE,
                 verbosity: int = 0):
        """Constructor. See parent for more information.

        :param load_function: Function that transforms machine-readable text
            into a Python structure. Used to unmarshall output of sub-parts
            of the module.
        :param dump_function: Function that transforms a Python structure into
            machine-readable text. Used to marshall the data from the
            hierarchy.
        """
        super().__init__(query, verbosity)

        self._load = load_function
        self._dump = dump_function

    @property
    def config(self):
        return SerializedPrinter.Config(
            query=self.query,
            verbosity=self.verbosity
        )
