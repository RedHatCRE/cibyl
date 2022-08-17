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
from dataclasses import dataclass
from typing import Optional

from overrides import overrides

from cibyl.cli.argument import Argument
from cibyl.models.attribute import AttributeListValue
from cibyl.models.ci.zuul.test_suite import TestSuite
from cibyl.models.model import Model


class Build(Model):
    """Representation of a build on a zuul environment.

    @DynamicAttrs: Contains attributes added on runtime.
    """

    @dataclass
    class Data:
        """Contains all information that defines a build for Cibyl.
        """
        uuid: str
        """ID of the build."""
        project: str
        """Name of the project the build belongs to."""
        pipeline: str
        """Name of the pipeline that triggered the build."""
        result: str
        """Result of the build."""
        duration: float
        """Time, in seconds, the build took to complete."""

    API = {
        'build_id': {
            'attr_type': str,
            'arguments': []
        },
        'project': {
            'attr_type': str,
            'arguments': []
        },
        'pipeline': {
            'attr_type': str,
            'arguments': []
        },
        'status': {
            'attr_type': str,
            'arguments': [
                Argument(
                    name='--build-status', arg_type=str,
                    func='get_builds', nargs='*',
                    description="Build status"
                )
            ]
        },
        'duration': {
            'attr_type': float,
            'arguments': [],
        },
        'suites': {
            'attr_type': TestSuite,
            'attribute_value_class': AttributeListValue,
            'arguments': [
                Argument(
                    name='--tests', arg_type=str,
                    nargs='*', func='get_tests',
                    description="Fetch build tests"
                )
            ]
        }
    }
    """Defines the contents of the model."""

    def __init__(self, data, suites=None):
        """Constructor.

        :param data: Data that defines this build.
        :type data: :class:`Build.Data`
        :param suites: Test suites under this build.
        :type suites: list[:class:`TestSuite`] or None
        """
        super().__init__(
            {
                'build_id': data.uuid,
                'project': data.project,
                'pipeline': data.pipeline,
                'status': data.result,
                'duration': data.duration,
                'suites': suites
            }
        )

    @overrides
    def __eq__(self, other):
        if not isinstance(other, Build):
            return False

        if self is other:
            return True

        return \
            self.build_id == other.build_id and \
            self.project == other.project and \
            self.pipeline == other.pipeline and \
            self.status == other.status and \
            self.duration == other.duration and \
            self.suites == other.suites

    def add_suite(self, suite: TestSuite) -> None:
        if self.get_suite(suite.name.value):
            return

        self.suites.append(suite)

    def get_suite(self, name: str) -> Optional[TestSuite]:
        for suite in self.suites:
            if name == suite.name.value:
                return suite

        return None

    def merge(self, other: 'Build') -> None:
        for suite in other.suites:
            self.add_suite(suite)
