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
from typing import Dict, List

from cibyl.cli.argument import Argument
from cibyl.models.attribute import AttributeDictValue, AttributeListValue
from cibyl.models.ci.base.stage import Stage
from cibyl.models.ci.base.test import Test
from cibyl.models.model import Model


class Build(Model):
    """General model for a job build

    @DynamicAttrs: Contains attributes added on runtime.
    """
    API = {
        'build_id': {
            'attr_type': str,
            'arguments': []
        },
        'status': {
            'attr_type': str,
            'arguments': [Argument(name='--build-status', arg_type=str,
                                   func='get_builds', nargs='*',
                                   description="Build status")]
        },
        'duration': {
            'attr_type': int,
            'arguments': [],
        },
        'tests': {
            'attr_type': Test,
            'attribute_value_class': AttributeDictValue,
            'arguments': [Argument(name='--tests', arg_type=str,
                                   nargs='*', func='get_tests',
                                   description="Job test")]
        },
        'stages': {
            'attr_type': Stage,
            'attribute_value_class': AttributeListValue,
            'arguments': [Argument(name='--stages', arg_type=str,
                                   nargs=0, description="Build stages run")]
            }
    }

    def __init__(self, build_id: str, status: str = None,
                 duration: int = None, tests: Dict[str, Test] = None,
                 stages: List[Stage] = None, **kwargs):
        if status is not None:
            status = status.upper()
        super().__init__({'build_id': build_id, 'status': status,
                          'duration': duration, 'tests': tests,
                          'stages': stages, **kwargs})

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.build_id.value == other.build_id.value

    def add_test(self, test: Test):
        """Add a test to the build.

        :param test: Test to add to the build
        :type test: Test
        """
        test_name = test.name.value
        if test_name in self.tests:
            self.tests[test_name].merge(test)
        else:
            self.tests[test_name] = test

    def add_stage(self, stage: Stage):
        """Add a stage to the build.

        :param stage: Stage to add to the build
        :type stage: Stage
        """
        self.stages.append(stage)

    def merge(self, other):
        """Merge the information of two build objects representing the same
        build.

        :param other: The Build object to merge
        :type other: :class:`.Build`
        """
        if not self.status.value:
            self.status.value = other.status.value
        for test in other.tests.values():
            self.add_test(test)
        if not self.stages.value and other.stages.value:
            self.stages = other.stages
