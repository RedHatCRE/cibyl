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
from cibyl.cli.argument import Argument
from cibyl.models.model import Model
from cibyl.utils.colors import Colors


class Test(Model):
    """General model for a build test."""
    API = {
        'name': {
            'attr_type': str,
            'arguments': [Argument(name='--test-name', arg_type=str,
                                   func='get_tests',
                                   description="Test name")]
        },
        'status': {
            'attr_type': str,
            'arguments': [Argument(name='--test-status', arg_type=str,
                                   func='get_tests',
                                   description="Test status")]
        },
        'duration': {
            'attr_type': int,
            'arguments': [Argument(name='--test-duration', arg_type=str,
                                   func='get_tests',
                                   description="Test duration")]
        },
    }

    def __init__(self, name: str, status: str = None,
                 duration: int = None):
        if status:
            status = status.upper()
        super().__init__({'name': name, 'status': status,
                          'duration': duration})

    def __str__(self, indent=0, verbosity=0):
        indent_space = indent*' '
        test_str = Colors.blue(
            f"{indent_space}Test: ") + f"{self.name.value}"
        if self.status.value:
            test_str += Colors.blue(f"\n{indent_space}  Status: ")
            if self.status.value == "SUCCESS":
                test_str += Colors.green(f"{self.status.value}")
            elif self.status.value == "FAILURE":
                test_str += Colors.red(f"{self.status.value}")
            elif self.status.value == "UNSTABLE":
                test_str += Colors.yellow(f"{self.status.value}")
            elif self.status.value == "SKIPPED":
                test_str += Colors.blue(f"{self.status.value}")

        if verbosity > 0 and self.duration.value:
            duration_in_min = self.duration.value / 60000
            test_str += Colors.blue(f"\n{indent_space}  Duration: ") + \
                f"{duration_in_min:.2f}m"
        return test_str

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.name.value == other.name.value

    def merge(self, other):
        """Merge the information of two test objects representing the same
        test.

        :param other: The Test object to merge
        :type other: :class:`.Test`
        """
        if not self.status.value:
            self.status.value = other.status.value
        if not self.duration.value:
            self.duration.value = other.duration.value
