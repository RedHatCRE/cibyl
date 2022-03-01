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
from cibyl.models.attribute import AttributeListValue, AttributeValue
from cibyl.models.ci.build import Build


class Job:
    """
        General model for a CI job. Holds basic information such as its
        name, builds and url.

    """
    def __init__(self, name: str, url: str = None):
        name_argument = Argument(name='--job-name', arg_type=str,
                                 description="Job name")
        self.name = AttributeValue(name="name", attr_type=str, value=name,
                                   arguments=[name_argument])
        url_argument = Argument(name='--job-url', arg_type=str,
                                description="Job URL")
        self.url = AttributeValue(name="url", attr_type=str, value=url,
                                  arguments=[url_argument])
        builds_argument = Argument(name='--builds', arg_type=str,
                                   description="Job builds")
        self.builds = AttributeListValue(name="builds",
                                         attr_type=Build,
                                         arguments=[builds_argument])

    def __str__(self):
        job_str = f"Job: {self.name.value}"
        if self.url.value:
            job_str += f"\n  URL: {self.url.value}"
        return job_str

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.name.value == other.name.value

    def add_build(self, build: Build):
        """Add a build to the job.

        :param build: Build to add to the job
        :type build: Build
        """
        self.builds.append(build)
