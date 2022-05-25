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

from cibyl.models.ci.zuul.test import Test, TestKind


class AnsibleTestStatus(IntEnum):
    """Possible results of an Ansible task.
    """
    UNKNOWN = 0
    """Could not determine how the task finished."""
    SUCCESS = 1
    """The task completed without errors."""
    FAILURE = 2
    """The task met an error it could not recover from."""
    SKIPPED = 3
    """The task was ignored."""
    CHANGED = 4
    """The task produced changes on the system."""


class AnsibleTest(Test):
    """Model for the execution of an Ansible task by a Zuul host.

    @DynamicAttrs: Contains attributes added on runtime.
    """

    class Data(Test.Data):
        """Holds the data that will define the model.
        """
        phase = 'UNKNOWN'
        """Phase on which the task was executed in."""
        host = 'UNKNOWN'
        """Target host for the task."""
        command = None
        """Command that it executed."""
        message = None
        """Returned message."""

    API = {
        **Test.API,
        'phase': {
            'attr_type': str,
            'arguments': []
        },
        'host': {
            'attr_type': str,
            'arguments': []
        },
        'command': {
            'attr_type': str,
            'arguments': []
        },
        'message': {
            'attr_type': str,
            'arguments': []
        }
    }
    """Defines base contents of the model."""

    def __init__(self, data=Data()):
        """Constructor.

        :param data: Defining data for this test.
        :type data: :class:`AnsibleTest.Data`
        """
        super().__init__(
            TestKind.ANSIBLE,
            data,
            **{
                'phase': data.phase,
                'host': data.host,
                'command': data.command,
                'message': data.message
            }
        )

    @overrides
    def __eq__(self, other):
        if not super().__eq__(other):
            return False

        # Check this model's additional fields
        return \
            self.phase == other.phase and \
            self.host == other.host and \
            self.command == other.command and \
            self.message == other.message
