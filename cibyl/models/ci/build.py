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
from cibyl.models.attribute import AttributeValue


class Build:
    """General model for a job build """
    def __init__(self, build_id: str, status: str = None):
        id_argument = Argument(name='--build-id', arg_type=str,
                               description="Build id")
        self.build_id = AttributeValue(name="build_id", attr_type=str,
                                       value=build_id, arguments=[id_argument])
        status_argument = Argument(name='--build-status', arg_type=str,
                                   description="Build status")
        self.status = AttributeValue(name="status", attr_type=str,
                                     value=status,
                                     arguments=[status_argument])

    def __str__(self):
        build_str = f"Build: {self.build_id.value}"
        if self.status.value:
            build_str += f"\n  Status: {self.status.value}"
        return build_str

    def __eq__(self, other):
        return self.build_id.value == other.build_id.value
