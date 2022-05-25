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
from enum import IntEnum

from overrides import overrides

from cibyl.models.ci.base.test import Test as BaseTest


class TestKind(IntEnum):
    """Defines the different kind of test cases known to Cibyl.
    """
    UNKNOWN = 0
    """Type is unknown, best effort will be tried."""
    ANSIBLE = 1
    """Test represents the execution of an Ansible task."""
    TEMPEST = 2
    """Test represents the execution of a Tempest test case."""


class TestStatus(IntEnum):
    """Default possible test results.
    """
    UNKNOWN = 0
    """Could not be determined the result of the test."""
    SUCCESS = 1
    """The test passed."""
    FAILURE = 2
    """Some condition in the test was not met."""
    SKIPPED = 3
    """The test was ignored."""


class Test(BaseTest):
    """Model for test cases on a Zuul environment.

    @DynamicAttrs: Contains attributes added on runtime.
    """

    class Data:
        """Holds the data that will define the model.
        """
        name = 'UNDEFINED'
        """Name of the test case."""
        status = TestStatus.UNKNOWN
        """Result of the test case."""
        duration = None
        """How long the test took to complete, in seconds."""
        url = None
        """Page where more information about the test can be obtained."""

    API = {
        **BaseTest.API,
        'kind': {
            'attr_type': TestKind,
            'arguments': []
        },
        'url': {
            'attr_type': str,
            'arguments': []
        }
    }
    """Defines base contents of the model."""

    def __init__(self, kind, data, **kwargs):
        """Constructor.

        :param kind: The type of test.
        :type kind: :class:`TestKind`
        :param data: Defining data for this test.
        :type data: :class:`Test.Data`
        :param kwargs: Additional data.
        :type kwargs: Any
        """
        super().__init__(
            name=data.name,
            result=data.status.name,
            duration=data.duration,
            kind=kind,
            url=data.url,
            **kwargs
        )

    @overrides
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        if self is other:
            return True

        return \
            self.kind == other.kind and \
            self.name == other.name and \
            self.result == other.result and \
            self.duration == other.duration and \
            self.url == other.url
