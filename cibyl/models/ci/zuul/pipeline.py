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
from cibyl.models.ci.zuul.job import Job
from cibyl.models.model import Model


class Pipeline(Model):
    """Representation of a Zuul pipeline.
    """
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
                    description='Jobs belonging to pipeline',
                    func='get_jobs'
                ),
                Argument(
                    name='--fetch-pipelines',
                    arg_type=str, nargs=0,
                    description='Show the job below the pipelines that '
                                'trigger it. '
                                'Warning, this operation may take long to '
                                'perform.'
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
        if not isinstance(other, Pipeline):
            return False

        if self.jobs != other.jobs:
            return False

        return self.name == other.name

    def merge(self, other):
        """Adds the contents of another pipeline into this one.

        :param other: The other pipeline.
        :type other: :class:`Pipeline`
        """
        for job in other.jobs.values():
            self.add_job(job)

    def add_job(self, job):
        """Appends, or merges, a new child job into this pipeline.

        If the job already exists in this pipeline, then it is not
        overwritten. Instead, the two jobs are merged together into a
        complete job model.

        :param job: The job to be added.
        :type job: :class:`Job`
        """
        key = job.name.value

        if key in self.jobs:
            # Extract unknown contents of job
            self.jobs[key].merge(job)
        else:
            # Register brand-new job
            self.jobs[key] = job
