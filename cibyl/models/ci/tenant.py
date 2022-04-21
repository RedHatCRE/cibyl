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
from cibyl.models.attribute import AttributeDictValue
from cibyl.models.ci.job import Job
from cibyl.models.model import Model


class Tenant(Model):
    API = {
        'name': {
            'attr_type': str,
            'arguments': []
        },
        'jobs': {
            'attr_type': Job,
            'attribute_value_class': AttributeDictValue,
            'arguments': [
                Argument(
                    name='--jobs',
                    arg_type=str, nargs='*',
                    description='Jobs belonging to tenant',
                    func='get_jobs'
                )
            ]
        }
    }

    def __init__(self, name, jobs=None):
        # Let IDEs know this model's attributes
        self.name = None
        self.jobs = None

        # Set up the model
        super().__init__({'name': name, 'jobs': jobs})

    def __eq__(self, other):
        if not isinstance(other, Tenant):
            return False

        return self.name == other.name

    def merge(self, other):
        """
        :param other:
        :type other: :class:`Tenant`
        :return:
        """
        for job in other.jobs:
            self._add_job(job)

    def _add_job(self, job):
        key = job.name.value

        if key in self.jobs:
            # Extract unknown contents of job
            self.jobs[key].merge(job)
        else:
            # Register brand-new job
            self.jobs[key] = job
