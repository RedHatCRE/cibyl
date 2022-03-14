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
        'build_id': {
            'attr_type': str,
            'arguments': [Argument(name='--build-id', arg_type=str,
                                   description="Build ID")]
        },
        'status': {
            'attr_type': str,
            'arguments': [Argument(name='--build-status', arg_type=str,
                                   description="Build status")]
        },
    }

    def __init__(self, build_id: str, status: str = None):
        super().__init__({'build_id': build_id, 'status': status})

    def __str__(self, indent=0):
        indent_space = indent*' '
        build_str = f"{indent_space}Build: {self.build_id.value}"
        if self.status.value:
            build_str += f"\n{indent_space}  Status: {self.status.value}"
        return build_str

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.build_id.value == other.build_id.value
