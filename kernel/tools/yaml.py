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
from typing import Any, Dict

import yaml
from overrides import overrides
from yaml import YAMLError as StandardYAMLError

YAML = Dict[str, Any]
"""Represents data originated from reading a YAML file."""


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
