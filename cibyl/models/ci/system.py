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

from cibyl.models.ci.job import Job
from cibyl.source import Source
from cibyl.value import ListValue, Value


class System:
    """
    """
    def __init__(self, name: str, type: str,
                 jobs=None, sources=None,
                 jobs_scope: str = None):
        """
        :param name:
        :param type:
        :param jobs:
        :param sources:
        :param jobs_scope:
        """
        self.name = Value(
            name='name', args=['--system-name'],
            type=str, data=name, description="the name of the system")

        self.type = Value(
            name='type', args=['--system-type'], type=str, data=type,
            description="system type (e.g. jenkins, zuul)")

        self.sources = ListValue(
            name='sources', args=['--sources'], type=Source, data=sources,
            nargs='*',
            description="source(s) name as specified in the config")

        self.jobs = ListValue(
            name='jobs', args=['--jobs', '--jobs-regex'],
            type=Job, data=jobs, nargs='*')

        self.jobs_scope = ListValue(name='jobs_scope', type=str,
                                    data=jobs_scope)

    def __str__(self, indent=0):
        """
        :param indent:
        :return:
        """
        output = "\n"
        output += " " * indent + crayons.green("system: ") + "{}".format(
            self.name.data)
        for job in self.jobs:
            output += "\n" + job.__str__(indent=indent + 2)
        return output
