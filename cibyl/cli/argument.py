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
import argparse
from typing import Iterable, List, Optional, Type, Union

from cibyl.cli.ranged_argument import (EXPRESSION_PATTERN, RANGE_OPERATORS,
                                       VALID_OPS, Range)
from cibyl.exceptions.cli import InvalidArgument


class Argument():
    """Represents Parser's argument"""

    # pylint: disable=too-many-arguments,too-many-instance-attributes
    def __init__(self, name: str, arg_type: Union[Type, argparse.FileType],
                 description: str, nargs: Union[str, int] = 1,
                 func: str = None, populated: bool = False, level: int = 0,
                 ranged: bool = False,
                 value: Union[List[str], List[Range]] = None,
                 default: object = None, choices: Optional[Iterable] = None):
        self.name = name

        self.arg_type = arg_type
        self.description = description
        self.nargs = nargs
        self.func = func
        self.populated = populated
        self.level = level
        self.ranged = ranged
        if self.ranged and value:
            self.value = self.parse_ranges(value)
        else:
            self.value = value
        self.default = default
        self.choices = choices

    def parse_ranges(self, expressions: List[str]) -> List[Range]:
        parsed_expressions = []
        if not isinstance(expressions, list):
            raise InvalidArgument(f"Argument '{self.name}' should accept "
                                  "multiple values")
        for expression in expressions:
            parsed_expression = EXPRESSION_PATTERN.search(expression)
            if not parsed_expression:
                raise InvalidArgument(f"Expression '{expression}' in argument "
                                      f"'{self.name}' is not valid")
            operator = parsed_expression.group(1)
            if not operator:
                operator = "=="
            if operator not in RANGE_OPERATORS:
                raise InvalidArgument(f"Operator '{operator}' in argument "
                                      f"'{self.name}' is not valid. Valid "
                                      f"operators include: {VALID_OPS}")
            operand = parsed_expression.group(2)
            parsed_expressions.append(Range(operator, operand))
        return parsed_expressions

    def __bool__(self):
        return bool(self.value)

    def __eq__(self, other):
        return self.name == other.name and self.value == other.value

    def __str__(self):
        return str(self.value)
