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


class Test(Model):
    """General model for a build test.

    @DynamicAttrs: Contains attributes added on runtime.
    """
    API = {
        'name': {
            'attr_type': str,
            'arguments': []
        },
        'result': {
            'attr_type': str,
            'arguments': [Argument(name='--test-result', arg_type=str,
                                   func='get_tests',
                                   nargs='*',
                                   description="Test result")]
        },
        'duration': {
            'attr_type': float,
            'arguments': [Argument(name='--test-duration', arg_type=str,
                                   func='get_tests', nargs='*',
                                   ranged=True,
                                   description="Test duration (in seconds)")]
        },
        'class_name': {
            'attr_type': str,
            'arguments': []
        }
    }

    def __init__(self, name: str, result: str = None,
                 duration: float = None, class_name: str = None, **kwargs):
        if result:
            result = result.upper()

        super().__init__(
            {
                'name': name,
                'result': result,
                'duration': duration,
                'class_name': class_name,
                **kwargs
            }
        )

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
