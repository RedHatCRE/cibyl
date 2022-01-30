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
from cibyl.value import ListValue
from cibyl.source import Source
from cibyl.models.ci.system import System
from cibyl.value import Value


class Environment(object):

    def __init__(self, name: str):

        self.name = Value(name='name', arg_name='--env-name', type=str,
                          data=name)
        self.systems = ListValue(name='systems', arg_name='--systems',
                                 type=System, data=[])

    def add_system(self, name, jobs=[], type=None, sources={}):
        source_instances = []
        for source_name, source_data in sources.items():
            source_instances.append(Source(name=source_name))
        self.systems.append(System(name=name, jobs=list(jobs),
                                   type=type, sources=source_instances))

    def __str__(self):
        output = ""
        output += self.name.data.replace('_', ' ').replace('-', ' ') + "\n  "
        for system in self.systems.data:
            output += system.__str__()
        return output
