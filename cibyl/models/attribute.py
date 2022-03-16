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
from cibyl.cli.argument import Argument


class AttributeValue():
    """Represents the value used by the attributes of the different models"""

    def __init__(self, name: str, attr_type: object,
                 value: object = None, arguments: list[Argument] = None):
        self.name = name
        self.attr_type = attr_type
        self.value = value
        self.arguments = arguments

    def __eq__(self, other):
        return self.name == other.name and self.value == other.value

    def __str__(self):
        return str(self.value)


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


class AttributeDictValue(AttributeValue):
    """Represents a dict of AttributeValue objects"""

    def __init__(self, name, arguments=None, attr_type=None, value=None):

        super().__init__(
            name=name, arguments=arguments, attr_type=attr_type, value=value)

        if isinstance(value, dict):
            self.value = value
        if value is None:
            self.value = {}

    def __setitem__(self, key, item):
        self.value[key] = item

    def __getitem__(self, key):
        return self.value[key]

    def __len__(self):
        return len(self.value)

    def __iter__(self):
        yield from self.value

    def items(self):
        """Return the value as key:value items"""
        return self.value.items()

    def values(self):
        """Return dictionary values"""
        return self.value.values()

    def keys(self):
        """Return dictionary values"""
        return self.value.keys()
