"""
Model different CI systems.
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

from cibyl.models.attribute import AttributeValue, AttributeListValue
from cibyl.models.ci.job import Job
from cibyl.models.ci.pipeline import Pipeline
from cibyl.cli.argument import Argument


class System:
    """
        General model for a CI system. Holds basic information such as its
        name, type and which pipelines and jobs it has.
    """

    def __init__(self, name: str, system_type: str):
        name_argument = Argument(name='--system-name', arg_type=str,
                                 description="System name")
        self.name = AttributeValue(name="name", attr_type=str, value=name,
                                   arguments=[name_argument])

        type_argument = Argument(name='--system-type', arg_type=str,
                                 description="System type")
        self.type = AttributeValue(name="type", attr_type=str,
                                   value=system_type,
                                   arguments=[type_argument])

        jobs_argument = Argument(name='--jobs', arg_type=str,
                                 description="System jobs")
        self.jobs = AttributeListValue(name="jobs", attr_type=Job,
                                       arguments=[jobs_argument])

    def __str__(self):
        return f"System {self.name.value} of type {self.type.value}"

    def add_job(self, job):
        """Add a job to the CI system

        :param job: Job to add to the system
        :type job: Job
        """
        self.jobs.append(job)


class ZuulSystem(System):
    """
        Model a Zuul CI system.
    """
    def __init__(self, name):
        super(ZuulSystem, self).__init__(name, "zuul")
        pipeline_argument = Argument(name='--pipelines', arg_type=str,
                                     description="System pipelines")
        self.pipelines = AttributeListValue(name="pipelines",
                                            attr_type=Pipeline,
                                            arguments=[pipeline_argument])

    def add_pipeline(self, pipeline):
        """Add a pipeline to the CI system

        :param pipeline: Pipeline to add to the system
        :type pipeline: Pipeline
        """
        self.pipelines.append(pipeline)


class JenkinsSystem(System):
    """
        Model a Jenkins CI system.
    """
    def __init__(self, name):
        super(JenkinsSystem, self).__init__(name, "jenkins")
