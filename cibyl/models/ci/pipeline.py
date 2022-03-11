# pylint: disable=no-member
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
from cibyl.models.attribute import AttributeListValue
from cibyl.models.ci.job import Job
from cibyl.models.model import Model


class Pipeline(Model):
    """Represents a Zuul pipeline"""

    API = {
        'name': {
            'attr_type': str,
            'arguments': [Argument(name='--pipeline-name', arg_type=str,
                                   description="System name")]
        },
        'jobs': {
            'attr_type': Job,
            'attribute_value_class': AttributeListValue,
            'arguments': [Argument(name='--jobs', arg_type=str,
                                   nargs='*',
                                   description="Pipeline jobs")]
        }
    }

    def __init__(self, name: str, jobs: list[Job] = None):
        super().__init__(attributes={'name': name,
                                     'jobs': jobs})

    def __str__(self, indent=0):
        indent_space = indent*' '
        string = f"{indent_space}Pipeline: {self.name.value}"
        for job in self.jobs:
            string += f"\n{job.__str__(indent=indent+2)}"
        return string

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.name.value == other.name.value
