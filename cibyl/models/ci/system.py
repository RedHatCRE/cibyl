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
        self.name = AttributeValue(name="name", attr_type=str, value=name,
                                   arguments=[Argument(name='--system-name', arg_type=str,
                                                       description="Name of the system")])
        self.type = AttributeValue(name="type", attr_type=str, value=system_type,
                                   arguments=[Argument(name='--system-type', arg_type=str,
                                                       description="Type of the system")])
        self.jobs = AttributeListValue(name="jobs", attr_type=Job,
                                       arguments=[Argument(name='--jobs', arg_type=str,
                                                           description="Jobs of the system")])

    def __str__(self):
        return f"System {self.name.value} of type {self.type.value}"

    def add_job(self, job):
        self.jobs.append(job)


class ZuulSystem(System):
    """
        Model a Zuul CI system.
    """
    def __init__(self, name):
        super(ZuulSystem, self).__init__(name, "zuul")
        self.pipelines = AttributeListValue(name="pipelines", attr_type=Pipeline,
                                            arguments=[Argument(name='--pipelines', arg_type=str,
                                                                description="Pipelines of the system")])

    def add_pipeline(self, pipeline):
        self.pipelines.append(pipeline)


class JenkinsSystem(System):

    def __init__(self, name):
        super(JenkinsSystem, self).__init__(name, "jenkins")
