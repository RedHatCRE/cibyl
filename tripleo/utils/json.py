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
from abc import ABC, abstractmethod
from typing import Union

from jsonschema.validators import Draft7Validator
from overrides import overrides

from tripleo.utils.fs import File

JSONValidator = Union[Draft7Validator]
"""Possible validators returned by the factory."""


class JSONValidatorFactory(ABC):
    """Base factory for all JSON validators.
    """

    @abstractmethod
    def from_file(self, file: File) -> JSONValidator:
        """Builds a new validator by reading the schema from a file.

        :param file: Path to the file to read.
        :return: New validator instance.
        :raise IOError: If the file could not be opened or read.
        :raise JSONDecodeError: If the file contents are not a valid JSON.
        :raise SchemaError: If the file contents are not a valid JSON schema.
        """
        raise NotImplementedError


class Draft7ValidatorFactory(JSONValidatorFactory):
    """Factory that generates validators capable of reading Draft-7 schemas.
    """

    @overrides
    def from_file(self, file: File) -> Draft7Validator:
        with open(file, 'r') as buffer:
            schema = json.loads(buffer.read())

            Draft7Validator.check_schema(schema)

            return Draft7Validator(schema)
