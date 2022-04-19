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
        'result': {
            'attr_type': str,
            'arguments': [Argument(name='--test-result', arg_type=str,
                                   func='get_tests',
                                   description="Test result")]
        },
        'duration': {
            'attr_type': int,
            'arguments': [Argument(name='--test-duration', arg_type=str,
                                   func='get_tests',
                                   description="Test duration")]
        },
        'class_name': {
            'attr_type': int,
            'arguments': [Argument(name='--test-class-name', arg_type=str,
                                   func='get_tests',
                                   description="Test class name")]
        }
    }

    def __init__(self, name: str, result: str = None,
                 duration: int = None, class_name: str = None):
        if result:
            result = result.upper()
        super().__init__({'name': name, 'result': result,
                          'duration': duration, 'class_name': class_name})

    def __str__(self, indent=0, verbosity=0):
        indent_space = indent*' '
        test_str = f"{indent_space}{Colors.blue('Test: ')}{self.name.value}"
        if self.result.value:
            test_str += f"\n{indent_space}  {Colors.blue('Result: ')}"
            success_values = ['SUCCESS', 'PASSED']
            failure_values = ['FAILURE', 'FAILED', 'REGRESSION']
            if self.result.value in success_values:
                test_str += Colors.green(f"{self.result.value}")
            elif self.result.value in failure_values:
                test_str += Colors.red(f"{self.result.value}")
            elif self.result.value == "UNSTABLE":
                test_str += Colors.yellow(f"{self.result.value}")
            elif self.result.value == "SKIPPED":
                test_str += Colors.blue(f"{self.result.value}")

        if self.class_name.value:
            test_str += f"\n{indent_space}  {Colors.blue('Class name: ')}"
            test_str += f"{self.class_name.value}"

        if verbosity > 0 and self.duration.value:
            duration_in_min = self.duration.value / 60000
            test_str += f"\n{indent_space}  {Colors.blue('Duration: ')}" + \
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
        if not self.result.value:
            self.result.value = other.result.value
        if not self.duration.value:
            self.duration.value = other.duration.value
        if not self.class_name.value:
            self.class_name.value = other.class_name.value
