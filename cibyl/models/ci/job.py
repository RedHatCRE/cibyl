"""
Model a CI job
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

from cibyl.cli.argument import Argument
from cibyl.models.attribute import AttributeValue


class Job:
    """
        General model for a CI job. Holds basic information such as its
        name, status and url.

    """
    def __init__(self, name: str, status: str, url: str):
        name_argument = Argument(name='--job-name', arg_type=str,
                                 description="Job name")
        self.name = AttributeValue(name="name", attr_type=str, value=name,
                                   arguments=[name_argument])
        status_argument = Argument(name='--job-status', arg_type=str,
                                   description="Job status")
        self.status = AttributeValue(name="status", attr_type=str,
                                     value=status,
                                     arguments=[status_argument])
        url_argument = Argument(name='--job-url', arg_type=str,
                                description="Job URL")
        self.url = AttributeValue(name="url", attr_type=str, value=url,
                                  arguments=[url_argument])

    def __str__(self):
        return f"Job {self.name.value} has status {self.status.value}"

    def __eq__(self, other):
        return self.name.value == other.name.value
