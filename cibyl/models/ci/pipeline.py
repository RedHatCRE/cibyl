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
from typing import Dict

from cibyl.cli.argument import Argument
from cibyl.models.attribute import AttributeDictValue
from cibyl.models.ci.job import Job
from cibyl.models.model import Model
from cibyl.utils.colors import Colors


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
            'attribute_value_class': AttributeDictValue,
            'arguments': [Argument(name='--jobs', arg_type=str, nargs='*',
                                   description="System jobs",
                                   func='get_jobs')]
        }
    }

    def __init__(self, name: str, jobs: Dict[str, Job] = None):
        super().__init__(attributes={'name': name,
                                     'jobs': jobs})

    def __str__(self, indent=0):
        indent_space = indent*' '
        string = Colors.blue(
            f"{indent_space}Pipeline: ") + f"{self.name.value}"
        for job in self.jobs:
            string += f"\n{job.__str__(indent=indent+2)}"
        string += f"\n{indent_space}" + \
            Colors.blue("Total jobs: ") + f"{len(self.jobs)}"
        return string

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.name.value == other.name.value

    def add_job(self, job: Job):
        """Add a job to the CI pipeline

        :param job: Job to add to the pipeline
        :type job: Job
        """
        name = job.name.value
        if name in self.jobs:
            self.jobs[name].merge(job)
        else:
            self.jobs[name] = job

    def merge(self, other):
        """Merge the information of two pipelines.

        :param other: The Pipeline object to merge
        :type other: :class:`.Pipeline`
        """
        for job in other.jobs.values():
            self.add_job(job)
