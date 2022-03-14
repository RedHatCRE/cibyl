"""
# Copyright 2022 Red Hat
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
from cibyl.models.attribute import AttributeListValue
from cibyl.models.ci.system import System
from cibyl.models.model import Model


class Environment(Model):
    """Represents a CI environment with one or more CI systems."""

    API = {
        'name': {
            'attr_type': str,
            'arguments': [Argument(name='--env-name', arg_type=str,
                                   description="Name of the environment")]
        },
        'systems': {
            'attr_type': System,
            'attribute_value_class': AttributeListValue,
            'arguments': [Argument(name='--systems', arg_type=str, nargs='*',
                                   description="Systems of the environment")]
        }
    }

    def __init__(self, name, systems=None):
        super().__init__({'name': name, 'systems': systems})

    def add_system(self, name: str, system_type: str, jobs_scope: str = None,
                   sources: list = None):
        """Adds a CI system to the CI environment"""
        self.systems.append(System(name=name, system_type=system_type,
                                   jobs_scope=jobs_scope, sources=sources))

    def __str__(self, indent=0):
        string = ""
        string += f"Environment: {self.name.value}"
        for system in self.systems:
            string += f"\n{system.__str__(indent + 2)}"
        return string
