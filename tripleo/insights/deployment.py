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

from tripleo.insights.types import YAML


class FeatureSetInterpreter:
    @dataclass
    class Keys:
        ipv6: str = 'overcloud_ipv6'

    def __init__(self, data: YAML, keys: Keys = Keys()):
        self._data = data
        self._keys = keys

    @property
    def data(self):
        return self._data

    @property
    def keys(self):
        return self._keys

    def is_ipv6(self) -> bool:
        key = self.keys.ipv6

        if key not in self.data:
            return False

        return self.data[key]
