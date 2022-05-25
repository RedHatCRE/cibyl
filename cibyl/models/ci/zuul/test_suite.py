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
from typing import List

from cibyl.models.ci.zuul.test import Test
from cibyl.models.model import Model


class TestSuite(Model):
    """
    @DynamicAttrs: Contains attributes added on runtime.
    """

    class Data:
        name = 'UNKNOWN'
        tests = []
        url = None

    API = {
        'name': {
            'attr_type': str,
            'arguments': []
        },
        'tests': {
            'attr_type': List[Test],
            'arguments': []
        },
        'url': {
            'attr_type': str,
            'arguments': []
        }
    }

    def __init__(self, data=Data()):
        super().__init__(
            {
                'name': data.name,
                'tests': data.tests,
                'url': data.url
            }
        )

    def __eq__(self, other):
        return False

    @property
    def test_count(self):
        return 0

    @property
    def success_count(self):
        return 0

    @property
    def failed_count(self):
        return 0

    @property
    def skipped_count(self):
        return 0

    @property
    def total_time(self):
        return 0
