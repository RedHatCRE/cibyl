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
from abc import abstractmethod
from typing import Dict, List

from cibyl.cli.argument import Argument
from cibyl.exceptions.model import NonSupportedModelType
from cibyl.models.attribute import AttributeDictValue, AttributeListValue
from cibyl.models.ci.job import Job
from cibyl.models.ci.pipeline import Pipeline
from cibyl.models.model import Model
from cibyl.sources.source import Source
from cibyl.utils.colors import Colors


class System(Model):
    """General model for a CI system.

    Holds basic information such as its name, type and which jobs it has.
    """
    API = {
        'name': {
            'attr_type': str,
            'arguments': []
        },
        'system_type': {
            'attr_type': str,
            'arguments': [Argument(name='--system-type', arg_type=str,
                                   description="System type")]
        },
        'queried': {
            'attr_type': bool,
            'arguments': []
        },
        'jobs_scope': {
            'attr_type': str,
            'arguments': []
        },
        'enabled': {
            'attr_type': bool,
            'arguments': []
        },
        'sources': {
            'attr_type': Source,
            'attribute_value_class': AttributeListValue,
            'arguments': [Argument(name='--sources', arg_type=str,
                                   nargs="*",
                                   description="Source name")]
        },
        'jobs': {'attr_type': Job,
                 'attribute_value_class': AttributeDictValue,
                 'arguments': [Argument(name='--jobs', arg_type=str,
                                        nargs='*',
                                        description="System jobs",
                                        func='get_jobs')]}
    }

    def __init__(self, name: str,  # pylint: disable=too-many-arguments
                 system_type: str, jobs: Dict[str, Job] = None,
                 jobs_scope: str = "*", sources: List = None,
                 pipelines: Dict[str, Pipeline] = None,
                 enabled: bool = True):
        super().__init__({'name': name, 'system_type': system_type,
                          'jobs': jobs, 'jobs_scope': jobs_scope,
                          'sources': sources, 'pipelines': pipelines,
                          'queried': False, 'enabled': enabled})
        # this variable describes which model will the system use as top-level
        # model. For most systems, this will be Job, for zuul systems it will
        # be Pipeline
        self.top_level_model = Job

    def enable(self):
        """Enable a system for querying."""
        self.enabled.value = True

    def is_enabled(self):
        """Check whether a system is enabled.

        :returns: Whether the system is enabled
        :rtype: bool
        """
        return self.enabled.value

    def register_query(self):
        """Record that the system was queried."""
        self.queried.value = True

    def is_queried(self):
        """Check whether a system was queried.

        :returns: Whether the system was queried
        :rtype: bool
        """
        return self.queried.value

    def add_source(self, source: Source):
        """Add a source to the CI system

        :param source: Source to add to the system
        :type source: Source
        """
        self.sources.append(source)

    @abstractmethod
    def add_toplevel_model(self, model: object):
        """Add a top-level model to the system. This will be different
        depending on the system type so it is left empty and will be overloaded
        by each type.
        """

    def populate(self, instances_dict):
        """Populate instances from a given dictionary of instances."""
        if instances_dict.attr_type == self.top_level_model:
            for model in instances_dict.values():
                self.add_toplevel_model(model)
        else:
            raise NonSupportedModelType(instances_dict.attr_type)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.name.value == other.name.value


class JobsSystem(System):
    """Model a system with Job as top-level model."""
    # make a copy so that it persists and we have the right attributes
    # if we later have to modify the System API
    API = System.API.copy()

    # pylint: disable=too-many-arguments
    def __init__(self, name: str, system_type: str,
                 jobs: Dict[str, Job] = None,
                 jobs_scope: str = "*", sources: List = None,
                 enabled: bool = True):

        super().__init__(name=name, system_type=system_type,
                         pipelines=None, jobs_scope=jobs_scope,
                         sources=sources, jobs=jobs, enabled=enabled)

    def add_toplevel_model(self, model: Job):
        """Add a top-level model to the system.

        :param job: Job to add to the system
        :type job: Job
        """
        self.add_job(model)

    def add_job(self, job: Job):
        """Add a job to the CI system

        :param job: Job to add to the system
        :type job: Job
        """
        job_name = job.name.value
        if job_name in self.jobs:
            self.jobs[job_name].merge(job)
        else:
            self.jobs[job_name] = job


class PipelineSystem(System):
    """Model a system with Pipeline as top-level model."""
    API = System.API.copy()
    API.pop('jobs')
    API['pipelines'] = {'attr_type': Pipeline,
                        'attribute_value_class': AttributeDictValue,
                        'arguments': [Argument(name='--pipelines',
                                               arg_type=str,
                                               nargs='*',
                                               description="System pipelines",
                                               func='get_pipelines')]}

    # pylint: disable=too-many-arguments
    def __init__(self, name: str, system_type: str,
                 pipelines: Dict[str, Pipeline] = None,
                 jobs_scope: str = "*", sources: List = None):

        super().__init__(name=name, system_type=system_type,
                         pipelines=pipelines, jobs_scope=jobs_scope,
                         sources=sources, jobs=None)
        self.top_level_model = Pipeline
        # if we have a pipeline-based system in the configuration, we need to
        # change the System hierarchy to include pipelines
        System.API = self.API

    def add_toplevel_model(self, model: Pipeline):
        """Add a top-level model to the system.

        :param pipeline: Pipeline to add to the system
        :type pipeline: Pipeline
        """
        self.add_pipeline(model)

    def add_pipeline(self, pipeline: Pipeline):
        """Add a pipeline to the CI system

        :param pipeline: Pipeline to add to the system
        :type pipeline: Pipeline
        """
        pipeline_name = pipeline.name.value
        if pipeline_name in self.pipelines:
            self.pipelines[pipeline_name].merge(pipeline)
        else:
            self.pipelines[pipeline_name] = pipeline

    def __str__(self, indent=0, verbosity=0):
        string = indent*' ' + Colors.blue("System: ") + f"{self.name.value}"
        if verbosity > 0:
            string += Colors.blue("type: ") + f"{self.system_type.value})"
        for pipeline in self.pipelines.values():
            string += f"\n{pipeline.__str__(indent+2, verbosity)}"
        return string
