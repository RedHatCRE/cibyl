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
import json
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
        """Parameters that define the behaviour of the printer.
        """
        query: QueryType
        """The type of query is gets to print."""
        palette: ColorPalette
        """Colors this will paint the output with."""
        verbosity: int
        """Verbosity level of the output."""

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
        """
        :return: Configuration for this printer.
        """
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
    """Base class for output styles based around serializing data.
    """

    @dataclass
    class Config:
        """Parameters that define the behaviour of the printer.
        """
        query: QueryType
        """The type of query is gets to print."""
        verbosity: int
        """Verbosity level of the output."""

    @dataclass
    class SerializationProvider:
        """Implementation of the marshaller / unmarshaller that the printer
        uses to go from models to text and back again.

        The provider must be able to go from data to the desired output
        format and back from that again. The printer unmarshalls pieces of
        the generated output in order to update it with more data.
        """
        load: Callable[[str], dict]
        """Transforms machine-readable text into a python structure."""
        dump: Callable[[dict], str]
        """Transforms a python structure into machine-readable text."""

    def __init__(self,
                 provider: SerializationProvider,
                 query: QueryType = QueryType.NONE,
                 verbosity: int = 0):
        """Constructor. See parent for more information.

        :param provider: Implementation of the serializer this uses to
        generate the output. This argument defines the format that the
        resulting text follows. For example, these could be implemented
        in JSON format for that output style to be supported. The printer
        remains generic enough so that only these functions decide
        how things are returned like.
        """
        super().__init__(query, verbosity)

        self._provider = provider

    @property
    def config(self) -> Config:
        """
        :return: Configuration for this printer.
        """
        return SerializedPrinter.Config(
            query=self.query,
            verbosity=self.verbosity
        )

    @property
    def provider(self):
        """
        :return: Serializing functions this uses to generate its output.
        """
        return self._provider


class JSONPrinter(SerializedPrinter):
    """Base class for printers that serialize data into JSON format.
    """

    @dataclass
    class Config(SerializedPrinter.Config):
        """Parameters that define the behaviour of the printer.
        """
        indentation: int
        """Number of spaces that indent each level of the JSON text."""

    def __init__(self,
                 query: QueryType = QueryType.NONE,
                 verbosity: int = 0,
                 indentation: int = 4):
        """Constructor. See parent for more information.

        :param indentation: Number of spaces that indent each level of the
            JSON output.
        """
        super().__init__(
            provider=SerializedPrinter.SerializationProvider(
                load=lambda obj: json.loads(obj),
                dump=lambda obj: json.dumps(obj, indent=self.indentation)
            ),
            query=query,
            verbosity=verbosity
        )

        self._indentation = indentation

    @property
    def config(self) -> Config:
        """
        :return: Configuration for this printer.
        """
        return JSONPrinter.Config(
            query=self.query,
            indentation=self.indentation,
            verbosity=self.verbosity
        )

    @property
    def indentation(self) -> int:
        """
        :return: Number of spaces preceding every level of the JSON output.
        """
        return self._indentation
