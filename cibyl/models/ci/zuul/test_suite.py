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
from cibyl.models.attribute import AttributeListValue
from cibyl.models.ci.zuul.test import Test, TestStatus
from cibyl.models.model import Model
from cibyl.utils.filtering import apply_filters


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
            'attr_type': Test,
            'attribute_value_class': AttributeListValue,
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
        if not isinstance(other, TestSuite):
            return False

        if self is other:
            return True

        return \
            self.name == other.name and \
            self.tests == other.tests and \
            self.url == other.url

    @property
    def test_count(self):
        return len(self.tests)

    @property
    def success_count(self):
        return len(
            apply_filters(
                self.tests,
                lambda test: test.status == TestStatus.SUCCESS
            )
        )

    @property
    def failed_count(self):
        return len(
            apply_filters(
                self.tests,
                lambda test: test.status == TestStatus.FAILURE
            )
        )

    @property
    def skipped_count(self):
        return len(
            apply_filters(
                self.tests,
                lambda test: test.status == TestStatus.SKIPPED
            )
        )

    @property
    def total_time(self):
        return sum(test.duration.value for test in self.tests)
