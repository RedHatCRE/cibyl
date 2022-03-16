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
from typing import Union


class Argument():
    """Represents Parser's argument"""

    # pylint: disable=too-many-arguments,too-many-instance-attributes
    def __init__(self, name: str, arg_type: object, description: str,
                 nargs: Union[str, int] = 1, func: str = None,
                 populated: bool = False, level: int = 0,
                 value: object = None, default: object = None):
        self.name = name
        self.arg_type = arg_type
        self.description = description
        self.nargs = nargs
        self.func = func
        self.populated = populated
        self.level = level
        self.value = value
        self.default = default

    def __eq__(self, other):
        return self.name == other.name and self.value == other.value

    def __str__(self):
        return str(self.value)
