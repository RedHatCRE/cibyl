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

from cibyl.cli.argument import Argument


@dataclass
class AttributeValue():
    """Represents the value used by the attributes of the different models"""

    name: str
    attr_type: object
    value: object
    arguments: list[Argument] = None


class AttributeListValue(AttributeValue):
    """Represents a list of AttributeValue objects"""

    def __init__(self, name, arguments=None, attr_type=None, value=None):

        super().__init__(
            name=name, arguments=arguments, attr_type=attr_type, value=value)

        if isinstance(value, list):
            self.value = value
        if value is None:
            self.value = []

    def append(self, item):
        """
        :param item:
        :return:
        """
        self.value.append(item)

    def __getitem__(self, index):
        """
        :param index:
        :return:
        """
        return self.value[index]
