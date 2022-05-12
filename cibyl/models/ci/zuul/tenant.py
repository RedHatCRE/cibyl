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
from cibyl.models.ci.zuul.project import Project
from cibyl.models.model import Model


class Tenant(Model):
    """Representation of a Zuul tenant.
    """
    API = {
        'name': {
            'attr_type': str,
            'arguments': []
        },
        'projects': {
            'attr_type': Project,
            'attribute_value_class': AttributeDictValue,
            'arguments': [
                Argument(
                    name='--projects',
                    arg_type=str, nargs='*',
                    description='Projects belonging to tenant',
                    func='get_projects'
                )
            ]
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

    def __init__(self, name, projects=None, jobs=None):
        # Let IDEs know this model's attributes
        self.name = None
        self.projects = None
        self.jobs = None

        # Set up the model
        super().__init__({'name': name, 'projects': projects, 'jobs': jobs})

    def __eq__(self, other):
        if not isinstance(other, Tenant):
            return False

        if self.projects != other.projects:
            return False

        if self.jobs != other.jobs:
            return False

        return self.name == other.name

    def merge(self, other):
        """Adds the contents of another tenant into this one.

        :param other: The other tenant.
        :type other: :class:`Tenant`
        """
        for project in other.projects.values():
            self.add_project(project)

        for job in other.jobs.values():
            self.add_job(job)

    def add_project(self, project):
        """Appends, or merges, a new child project into this tenant.

        If the project already exists in this tenant, then it is not
        overwritten. Instead, the two projects are merged together into a
        complete project model.

        :param project: The project to be added.
        :type project: :class:`Project`
        """
        key = project.name.value

        if key in self.projects:
            # Extract unknown contents of project
            self.projects[key].merge(project)
        else:
            # Register brand-new project
            self.projects[key] = project

    def add_job(self, job):
        """Appends, or merges, a new child job into this tenant.

        If the job already exists in this tenant, then it is not
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
