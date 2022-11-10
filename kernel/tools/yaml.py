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
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

import yaml
from cached_property import cached_property
from overrides import overrides
from yaml import YAMLError as StandardYAMLError

from kernel.tools.fs import File, KnownDirs, cd
from kernel.tools.json import Draft7ValidatorFactory, JSONValidatorFactory

YAMLObj = Dict[str, Any]
"""Represents an object on a YAML file."""
YAMLArray = List[YAMLObj]
"""Represents an array on a YAML file."""
YAML = Union[YAMLArray, YAMLObj]
"""Represents data originated from a YAML file."""


class YAMLError(Exception):
    """Describes any errors that happened while parsing a stream in YAML
    format.
    """


class YAMLParser(ABC):
    """Base class for all tools that transform some stream in YAML format
    into a Python object.
    """

    @abstractmethod
    def as_yaml(self, string: str) -> YAML:
        """
        :param string: Text in YAML format.
        :return: The corresponding Python object.
        :raises YAMLError: If the text is not in YAML format.
        """
        raise NotImplementedError


class StandardYAMLParser(YAMLParser):
    """Implementation of a YAML parser that uses Python's standard library.
    """

    @overrides
    def as_yaml(self, string: str) -> YAML:
        try:
            return yaml.safe_load(string)
        except StandardYAMLError as ex:
            msg = f"Failed to parse text: '{string}'."
            raise YAMLError(msg) from ex


class YAMLFile:
    """Representation of YAML-like file.
    """

    @dataclass
    class Tools:
        """Tools this uses to do its task.
        """
        parser: YAMLParser = field(
            default_factory=lambda *_: StandardYAMLParser()
        )
        """Used to translate the data in the file into python-readable."""
        validators: JSONValidatorFactory = field(
            default_factory=lambda *_: Draft7ValidatorFactory()
        )
        """Used to face the data in the file against an schema."""

    def __init__(
        self,
        file: File,
        schema: Optional[File] = None,
        tools: Optional[Tools] = None
    ):
        """Constructor.

        :param file:
            The YAML file to have this class wrap around.
        :param schema:
            Schema that the data in the file must meet.
            'None' to ignore.
        :param tools:
            Selection of tools this uses to do its task.
            'None' to have this build its own.
        :raises YAMLError:
            If the data is not in YAML format.
            If the data does not meet the schema.
        """
        if tools is None:
            tools = YAMLFile.Tools()

        self._file = file
        self._schema = schema
        self._tools = tools

        self._validate()

    def _validate(self):
        """Checks that the file meets the given schema. Throws an error if it
        does not, returns if it does. In case no schema was provided, this does
        nothing.

        :raises YAMLError: If the data does not meet the schema.
        """
        if self.schema is None:
            return

        with cd(KnownDirs.CIBYL):
            validator = self.tools.validators.from_file(self.schema)

            if validator.is_valid(self.data):
                return

        raise YAMLError(
            f"File: '{self.file}' does not conform to schema: '{self.schema}'."
        )

    @cached_property
    def data(self) -> YAML:
        """
        :return: Raw data found within the file, verified against the schema.
        """
        return self.tools.parser.as_yaml(self.file.read())

    @property
    def file(self) -> File:
        """
        :return: The YAML file this is handling.
        """
        return self._file

    @property
    def schema(self) -> Optional[File]:
        """
        :return: The schema met by the file. 'None' if this was skipped.
        """
        return self._schema

    @property
    def tools(self) -> Tools:
        """
        :return: Tools this uses to do its task.
        """
        return self._tools
