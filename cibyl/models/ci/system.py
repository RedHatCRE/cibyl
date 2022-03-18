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
# pylint: disable=no-member
from typing import Dict, List

from cibyl.cli.argument import Argument
from cibyl.exceptions.model import NonSupportedModelType
from cibyl.models.attribute import AttributeDictValue, AttributeListValue
from cibyl.models.ci.job import Job
from cibyl.models.ci.pipeline import Pipeline
from cibyl.models.model import Model
from cibyl.sources.source import Source


class System(Model):
    """General model for a CI system.

    Holds basic information such as its name, type and which jobs it has.
    """
    API = {
        'name': {
            'attr_type': str,
            'arguments': [Argument(name='--system-name', arg_type=str,
                                   description="System name")]
        },
        'system_type': {
            'attr_type': str,
            'arguments': [Argument(name='--system-type', arg_type=str,
                                   description="System type")]
        },
        'jobs': {
            'attr_type': Job,
            'attribute_value_class': AttributeDictValue,
            'arguments': [Argument(name='--jobs', arg_type=str, nargs='*',
                                   description="System jobs",
                                   func='get_jobs')]
        },
        'jobs_scope': {
            'attr_type': str,
            'arguments': []
        },
        'sources': {
            'attr_type': Source,
            'attribute_value_class': AttributeListValue,
            'arguments': [Argument(name='--sources', arg_type=str,
                                   nargs="*",
                                   description="Source name")]
        }
    }

    def __init__(self, name: str,  # pylint: disable=too-many-arguments
                 system_type: str, jobs: Dict[str, Job] = None,
                 jobs_scope: str = "*", sources: List = None):
        super().__init__({'name': name, 'system_type': system_type,
                          'jobs': jobs, 'jobs_scope': jobs_scope,
                          'sources': sources})

    def __str__(self, indent=0, verbosity=0):
        string = indent*' ' + f"System: {self.name.value}"
        if verbosity > 0:
            string += f" (type: {self.system_type.value})"
        for job in self.jobs.values():
            string += f"\n{job.__str__(indent+2, verbosity)}"
        return string

    def populate(self, instances_dict):
        """Populate instances from a given dictionary of instances."""
        if instances_dict.attr_type == Job:
            for job in instances_dict.values():
                self.add_job(job)
        else:
            raise NonSupportedModelType(instances_dict.attr_type)

    def add_job(self, job: Job):
        """Add a job to the CI system

        :param job: Job to add to the system
        :type job: Job
        """
        job_name = job.name.value
        if job_name in self.jobs.values():
            self.jobs[job_name].merge(job)
        else:
            self.jobs[job_name] = job

    def add_source(self, source: Source):
        """Add a source to the CI system

        :param source: Source to add to the system
        :type source: Source
        """
        self.sources.append(source)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.name.value == other.name.value


class ZuulSystem(System):
    """Model a Zuul CI system."""
    def __init__(self, name: str):
        super().__init__(name, "zuul")
        pipeline_argument = Argument(name='--pipelines', arg_type=str,
                                     description="System pipelines")
        self.pipelines = AttributeDictValue(name="pipelines",
                                            attr_type=Pipeline,
                                            arguments=[pipeline_argument])

    def add_pipeline(self, pipeline: Pipeline):
        """Add a pipeline to the CI system

        :param pipeline: Pipeline to add to the system
        :type pipeline: Pipeline
        """
        pipeline_name = pipeline.name.value
        if pipeline_name in self.pipelines.values():
            self.pipelines[pipeline_name].merge(pipeline)
        else:
            self.pipelines[pipeline_name] = pipeline


class JenkinsSystem(System):
    """Model a Jenkins CI system."""
    def __init__(self, name: str):
        super().__init__(name, "jenkins")

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.name.value == other.name.value
