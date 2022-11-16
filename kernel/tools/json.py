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
from dataclasses import dataclass, field
from typing import Optional, Union

from jsonschema.validators import Draft7Validator
from overrides import overrides

from kernel.tools.cache import CACache, Cache
from kernel.tools.fs import File
from kernel.tools.net import download_into_memory
from kernel.tools.urls import URL

JSONValidator = Union[Draft7Validator]
"""Possible validators returned by the factory."""


class JSONValidatorFactory(ABC):
    """Base factory for all JSON validators.
    """

    @dataclass
    class Caches:
        files: Cache[File, JSONValidator] = field(
            default_factory=lambda *_: CACache()
        )
        remotes: Cache[URL, JSONValidator] = field(
            default_factory=lambda *_: CACache()
        )

    def __init__(self, caches: Optional[Caches] = None):
        if caches is None:
            caches = JSONValidatorFactory.Caches()

        self._caches = caches

    @property
    def caches(self) -> Caches:
        return self._caches

    @abstractmethod
    def from_buffer(self, buffer: Union[bytes, str]) -> JSONValidator:
        raise NotImplementedError

    def from_file(self, file: File, encoding: str = 'utf-8') -> JSONValidator:
        """Builds a new validator by reading the schema from a file.

        :param file: Path to the file to read.
        :param encoding: Name of the file encoding, like in built-in 'open'.
        :return: New validator instance.
        :raise IOError: If the file could not be opened or read.
        :raise JSONDecodeError: If the file contents are not a valid JSON.
        :raise SchemaError: If the file contents are not a valid JSON schema.
        """
        cache = self.caches.files

        if cache.has(file):
            return cache.get(file)

        with open(file, 'r', encoding=encoding) as buffer:
            validator = self.from_buffer(buffer.read())
            cache.put(file, validator)
            return validator

    def from_remote(self, url: URL) -> JSONValidator:
        cache = self.caches.remotes

        if cache.has(url):
            return cache.get(url)

        validator = self.from_buffer(download_into_memory(url))
        cache.put(url, validator)
        return validator


class Draft7ValidatorFactory(JSONValidatorFactory):
    """Factory that generates validators capable of reading Draft-7 schemas.
    """

    @overrides
    def from_buffer(self, buffer: Union[bytes, str]) -> Draft7Validator:
        schema = json.loads(buffer)

        Draft7Validator.check_schema(schema)

        return Draft7Validator(schema)
