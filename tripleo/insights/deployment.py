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
from typing import Dict, Optional

from tripleo.insights.exceptions import IllegibleData
from tripleo.utils.json import Draft7ValidatorFactory, JSONValidatorFactory
from tripleo.utils.types import YAML, File


class FileInterpreter(ABC):
    def __init__(
        self,
        data: YAML,
        schema: File,
        overrides: Optional[Dict] = None,
        validator_factory: JSONValidatorFactory = Draft7ValidatorFactory()
    ):
        """Constructor.

        :param data: Contents of the file, parsed from YAML format.
        :param schema: The structure that the file must follow.
        :param validator_factory: Creates the validator used to check the
            data against the schema.
        :raises IOError: If the schema file does not exist or cannot be opened.
        :raises IllegibleData:
            If the data does not match the schema.
            If the 'overrides' dictionary does not match the schema.
        """

        def validate_data(__data):
            if not validator.is_valid(__data):
                raise IllegibleData('Data does not conform to its schema.')

        if overrides is None:
            overrides = {}

        validator = validator_factory.from_file(schema)

        validate_data(data)
        validate_data(overrides)

        self._data = data
        self._overrides = overrides

    @property
    def data(self) -> YAML:
        """
        :return: Raw data contained by the file.
        """
        return self._data

    @property
    def overrides(self):
        return self._overrides


class EnvironmentInterpreter(FileInterpreter):
    @dataclass
    class Keys:
        infra_type: str = 'environment_type'

    KEYS = Keys()

    def __init__(
        self,
        data: YAML,
        schema: File = File('tripleo/_data/schemas/environment.json'),
        overrides: Optional[Dict] = None,
        validator_factory: JSONValidatorFactory = Draft7ValidatorFactory()
    ):
        super().__init__(data, schema, overrides, validator_factory)

    def get_intra_type(self) -> Optional[str]:
        key = self.KEYS.infra_type

        if key in self.overrides:
            return self.overrides[key]

        if key in self.data:
            return self.data[key]

        return None


class FeatureSetInterpreter(FileInterpreter):
    """Takes care of making sense out of the contents of a featureset file.
    """

    @dataclass
    class Keys:
        """Defines the fields of interest contained by a featureset file.
        """
        ipv6: str = 'overcloud_ipv6'
        """Indicates IP version of deployment."""

    KEYS = Keys()
    """Knowledge that this has about the featureset file's contents."""

    def __init__(
        self,
        data: YAML,
        schema: File = File('tripleo/_data/schemas/featureset.json'),
        overrides: Optional[Dict] = None,
        validator_factory: JSONValidatorFactory = Draft7ValidatorFactory()
    ):
        super().__init__(data, schema, overrides, validator_factory)

    def is_ipv6(self) -> bool:
        """
        :return: True if the deployment works under IPv6, False if it does
            under IPv4.
        """
        key = self.KEYS.ipv6

        if key in self.overrides:
            return self.overrides[key]

        if key in self.data:
            return self.data[key]

        return False
