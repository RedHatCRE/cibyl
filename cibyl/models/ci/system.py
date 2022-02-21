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


class System:
    """
        General model for a CI system. Holds basic information such as its
        name, type and which pipelines and jobs it has.
    """

    def __init__(self, name: str, type_system: str):
        self.name = AttributeValue(name="name", type=str, value=name,
                                   arguments=['--system-name'])
        self.type = AttributeValue(name="type", type=str, value=type_system,
                                   arguments=['--system-type'])
        self.pipelines = AttributeListValue(name="pipelines", type=Pipeline,
                                            arguments=['--pipelines'])
        self.jobs = AttributeListValue(name="jobs", type=Job,
                                       arguments=['--jobs'])

    def __str__(self):
        return f"System {self.name.value} of type {self.type.value}"

    def add_job(self, job):
        self.jobs.append(job)

    def add_pipeline(self, pipeline):
        self.pipelines.append(pipeline)


class ZuulModel(System):
    """
        Model a Zuul CI system.
    """
    def __init__(self, name):
        super(ZuulModel, self).__init__(name, "zuul")


class JenkinsModel(System):

    def __init__(self, name):
        super(JenkinsModel, self).__init__(name, "jenkins")
