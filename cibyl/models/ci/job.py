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
import crayons

from cibyl.models.ci.test import Test
from cibyl.value import ListValue, Value


class Job:
    """
    """

    def __init__(self, name: str):
        """
        :param name:
        """
        self.name = Value(name='name', args=['--job-name'],
                          type=str, data=name)
        self.tests = ListValue(name='tests', args=['--tests'],
                               type=Test)

    def __str__(self, indent=0):
        """
        :param indent:
        :return:
        """
        output = ""
        output += " " * indent + crayons.green("job: ") + "{}".format(
            self.name.data)
        return output
