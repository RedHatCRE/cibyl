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
from dataclasses import dataclass

from tripleo.utils.json import Draft7ValidatorFactory, JSONValidatorFactory
from tripleo.utils.types import YAML, Path


class FeatureSetInterpreter:
    @dataclass
    class Keys:
        ipv6: str = 'overcloud_ipv6'

    KEYS = Keys()

    def __init__(
        self,
        data: YAML,
        schema: Path = Path('tripleo/_data/schemas/featureset.json'),
        validator_factory: JSONValidatorFactory = Draft7ValidatorFactory()
    ):
        validator = validator_factory.from_file(schema.to_str())

        if not validator.is_valid(data):
            msg = 'Featureset data does not conform to its schema.'
            raise ValueError(msg)

        self._data = data

    @property
    def data(self):
        return self._data

    def is_ipv6(self) -> bool:
        key = self.KEYS.ipv6

        if key not in self.data:
            return False

        return self.data[key]
