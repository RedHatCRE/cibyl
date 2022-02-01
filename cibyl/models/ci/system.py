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
from cibyl.models.ci.job import Job
from cibyl.source import Source
from cibyl.value import Value

import crayons


class System(object):

    def __init__(self, name: str, type: str,
                 jobs=None, sources=None,
                 jobs_scope: str = None):

        self.name = Value(name='name', arg_name='--system-name',
                          type=str, data=name)
        self.type = Value(name='type', arg_name='--system-type',
                          type=str, data=type)
        self.sources = ListValue(name='sources', arg_name='--sources',
                                 type=Source, data=sources)
        self.jobs = ListValue(name='jobs', arg_name='--jobs',
                              type=Job, data=jobs, nargs='*')
        self.jobs_scope = ListValue(name='jobs_scope', type=str)

    def __str__(self):
        output = ""
        output += "  " + crayons.green("system: ") + "{}\n".format(
            self.name.data)
        for job in self.jobs:
            output += job.__str__()
        return output
