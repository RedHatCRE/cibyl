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
import crayons

from cibyl.models.ci.system import System
from cibyl.source import Source
from cibyl.value import ListValue, Value


class Environment:
    """
    """
    def __init__(self, name: str):
        """
        Initialize Environment class
        :param name:
        """
        self.name = Value(name='name', args=['--env-name'], type=str,
                          data=name, description="the name of the environment")

        self.systems = ListValue(name='systems', args=['--systems'],
                                 type=System,
                                 description="the environment systems")

    def add_system(self, name, jobs_scope=None, type=None, sources=None):
        """
        :param name:
        :param jobs_scope:
        :param type:
        :param sources:
        :return:
        """
        if sources is None:
            sources = {}
        source_instances = []
        if isinstance(jobs_scope, str):
            jobs_scope = jobs_scope.split(" ")

        # Create source instances
        for source_name, source_dict in sources.items():
            source_instances.append(
                Source(name=source_name, **source_dict))

        # Add System instance
        self.systems.append(
            System(name=name, jobs_scope=jobs_scope, type=type,
                   sources=source_instances))

    def __str__(self, indent=0):
        """
        :param indent:
        :return:
        """
        output = ""
        output += crayons.green("environment: ") + self.name.data.replace(
            '_', ' ').replace('-', ' ')
        for system in self.systems.data:
            output += system.__str__(indent=indent + 2)
        return output + "\n"
