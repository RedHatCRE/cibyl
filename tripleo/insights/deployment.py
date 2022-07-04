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
from typing import Optional

from tripleo.insights.exceptions import IllegibleData
from tripleo.utils.json import Draft7ValidatorFactory, JSONValidatorFactory
from tripleo.utils.types import YAML, File


class FileInterpreter(ABC):
    def __init__(
        self,
        data: YAML,
        schema: File,
        validator_factory: JSONValidatorFactory = Draft7ValidatorFactory()
    ):
        """Constructor.

        :param data: Contents of the file, parsed from YAML format.
        :param schema: The structure that the file must follow.
        :param validator_factory: Creates the validator used to check the
            data against the schema.
        :raises IOError: If the schema file does not exist or cannot be opened.
        :raises IllegibleData: If the data does not match the schema.
        """
        schema.check_exists()

        validator = validator_factory.from_file(schema)

        if not validator.is_valid(data):
            msg = 'Data does not conform to its schema.'
            raise IllegibleData(msg)

        self._data = data

    @property
    def data(self) -> YAML:
        """
        :return: Raw data contained by the file.
        """
        return self._data


class EnvironmentInterpreter(FileInterpreter):
    @dataclass
    class Keys:
        infra_type: str = 'environment_type'

    KEYS = Keys()

    def __init__(
        self,
        data: YAML,
        schema: File = File('tripleo/_data/schemas/environment.json'),
        validator_factory: JSONValidatorFactory = Draft7ValidatorFactory()
    ):
        super().__init__(data, schema, validator_factory)

    def get_intra_type(self) -> Optional[str]:
        key = self.KEYS.infra_type

        if key not in self.data:
            return None

        return self.data[key]


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
        validator_factory: JSONValidatorFactory = Draft7ValidatorFactory()
    ):
        super().__init__(data, schema, validator_factory)

    def is_ipv6(self) -> bool:
        """
        :return: True if the deployment works under IPv6, False if it does
            under IPv4.
        """
        key = self.KEYS.ipv6

        if key not in self.data:
            return False

        return self.data[key]
