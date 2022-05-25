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


class TempestTestStatus(IntEnum):
    UNKNOWN = 0
    SUCCESS = 1
    FAILURE = 2
    ERROR = 3
    SKIPPED = 4


class TempestTest(Test):
    class Data(Test.Data):
        class_name = 'UNKNOWN'
        skip_reason = None

    API = {
        **Test.API,
        'class_name': {
            'attr_type': str,
            'arguments': []
        },
        'skip_reason': {
            'attr_type': str,
            'arguments': []
        }
    }

    def __init__(self, data=Data()):
        super().__init__(
            TestKind.TEMPEST,
            data,
            **{
                'class_name': data.class_name,
                'skip_reason': data.skip_reason
            }
        )

    @overrides
    def __eq__(self, other):
        if not super().__eq__(other):
            return False

        # Check this model's additional fields
        return \
            self.class_name == other.class_name and \
            self.skip_reason == other.skip_reason
