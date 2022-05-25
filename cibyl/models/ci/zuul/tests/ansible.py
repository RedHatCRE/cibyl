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
    UNKNOWN = 0
    SUCCESS = 1
    FAILURE = 2
    CHANGED = 3
    SKIPPED = 4


class AnsibleTest(Test):
    class Data(Test.Data):
        phase = 'UNKNOWN'
        host = 'UNKNOWN'
        command = None
        message = None

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

    def __init__(self, data):
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

        # Check additional fields of this test
        return \
            self.phase == other.phase and \
            self.host == other.host and \
            self.command == other.command and \
            self.message == other.message
