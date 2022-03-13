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
# pylint: disable=no-member
from cibyl.cli.argument import Argument
from cibyl.models.model import Model


class Build(Model):
    """General model for a job build """
    API = {
        'number': {
            'attr_type': str,
            'arguments': [Argument(name='--build-number', arg_type=str,
                                   description="Build ID")]
        },
        'result': {
            'attr_type': str,
            'arguments': [Argument(name='--build-result', arg_type=str,
                                   description="Build result")]
        },
    }

    def __init__(self, number: str, result: str = None):
        super().__init__({'number': number, 'result': result})

    def __str__(self, indent=0):
        indent_space = indent*' '
        build_str = f"{indent_space}Build: {self.number.value}"
        if self.result.value:
            build_str += f"\n{indent_space}  result: {self.result.value}"
        return build_str

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.number.value == other.number.value
