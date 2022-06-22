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
from typing import Iterator, List

from cibyl.cli.argument import Argument


class AttributeValue:
    """Represents the value used by the attributes of the different models"""

    def __init__(self, name: str, attr_type: object,
                 value: object = None,
                 arguments: List[Argument] = None) -> None:
        self.name = name
        self.attr_type = attr_type
        self.value = value
        self.arguments = arguments

    def __bool__(self) -> bool:
        return bool(self.value)

    def __eq__(self, other: 'AttributeValue') -> bool:
        return self.name == other.name and self.value == other.value

    def __str__(self) -> str:
        return str(self.value)


class AttributeListValue(AttributeValue):
    """Represents a list of AttributeValue objects"""

    def __init__(self, name: str, arguments: List[Argument] = None,
                 attr_type: object = None, value: object = None) -> None:

        super().__init__(
            name=name, arguments=arguments, attr_type=attr_type, value=value)

        if isinstance(value, list):
            self.value = value
        if value is None:
            self.value = []

    def append(self, item: object) -> None:
        """
        :param item:
        :return:
        """
        self.value.append(item)

    def __getitem__(self, index: int) -> object:
        """
        :param index:
        :return:
        """
        return self.value[index]

    def __len__(self) -> int:
        return len(self.value)


class AttributeDictValue(AttributeValue):
    """Represents a dict of AttributeValue objects"""

    def __init__(self, name: str, arguments: List['Argument'] = None,
                 attr_type: object = None, value: object = None) -> None:

        super().__init__(
            name=name, arguments=arguments, attr_type=attr_type, value=value)

        if isinstance(value, dict):
            self.value = value
        if value is None:
            self.value = {}

    def __setitem__(self, key: object, item: object) -> None:
        self.value[key] = item

    def __getitem__(self, key: object) -> object:
        return self.value[key]

    def __len__(self) -> int:
        return len(self.value)

    def __iter__(self) -> Iterator[object]:
        yield from self.value

    def __delitem__(self, key: object) -> object:
        del self.value[key]

    def items(self) -> dict:
        """Return the value as key:value items"""
        return self.value.items()

    def values(self) -> List[object]:
        """Return dictionary values"""
        return self.value.values()

    def keys(self) -> List[object]:
        """Return dictionary values"""
        return self.value.keys()

    def get(self, key: object, default: object = None) -> object:
        return self.value.get(key, default)
