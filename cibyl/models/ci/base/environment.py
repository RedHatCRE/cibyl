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
from cibyl.models.ci.base.system import System
from cibyl.models.ci.system_factory import SystemFactory
from cibyl.models.model import Model


class Environment(Model):
    """Represents a CI environment with one or more CI systems."""

    API = {
        'name': {
            'attr_type': str,
            'arguments': [Argument(name='--envs', arg_type=str,
                                   description="Environment names")]
        },
        'systems': {
            'attr_type': System,
            'attribute_value_class': AttributeListValue,
            'arguments': [Argument(name='--systems', arg_type=str, nargs='*',
                                   description="Systems names")]
        },
        'enabled': {
            'attr_type': bool,
            'arguments': []
        },
    }

    def __init__(self, name, systems=None, enabled=True):
        # Let IDEs know this model's attributes
        self.name = None
        self.systems = None
        self.enabled = None

        super().__init__({'name': name, 'systems': systems,
                          'enabled': enabled})

    def add_system(self,
                   name: str, system_type: str,
                   sources: list = None, enabled: bool = True, **kwargs):
        """Adds a CI system to the CI environment"""
        self.systems.append(
            SystemFactory.create_system(
                system_type, name,
                sources=sources,
                enabled=enabled,
                **kwargs
            )
        )
