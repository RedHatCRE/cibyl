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

from cibyl.models.model import Model


class TestKind(IntEnum):
    UNKNOWN = 0
    ANSIBLE = 1
    TEMPEST = 2


class TestStatus(IntEnum):
    UNKNOWN = 0
    SUCCESS = 1
    FAILURE = 2


class Test(Model):
    """
    @DynamicAttrs: Contains attributes added on runtime.
    """

    class Data:
        name = 'UNDEFINED'
        status = TestStatus.UNKNOWN
        duration = None
        url = None

    API = {
        'kind': {
            'attr_type': TestKind,
            'arguments': []
        },
        'name': {
            'attr_type': str,
            'arguments': []
        },
        'status': {
            'attr_type': int,
            'arguments': []
        },
        'duration': {
            'attr_type': float,
            'arguments': []
        },
        'url': {
            'attr_type': str,
            'arguments': []
        }
    }

    def __init__(self, kind, data, **kwargs):
        super().__init__(
            {
                'kind': kind,
                'name': data.name,
                'status': data.status,
                'duration': data.duration,
                'url': data.url,
                **kwargs
            }
        )

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        if self is other:
            return True

        return \
            self.kind == other.kind and \
            self.name == other.name and \
            self.status == other.status and \
            self.duration == other.duration and \
            self.url == other.url
