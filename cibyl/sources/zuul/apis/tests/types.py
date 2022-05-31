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
from dataclasses import dataclass, field
from typing import List, Optional, Union

from cibyl.sources.zuul.apis.tests.ansible.types import AnsibleTest

Test = Union[AnsibleTest]
"""Defines all possible types of test known to Cibyl."""


@dataclass
class TestSuite:
    """Collection on test cases that have something in common.
    """
    name: str
    """Name of the suite."""
    url: Optional[str] = None
    """Page where to get more information about the tests."""
    tests: List[Test] = field(default_factory=lambda: [])
    """Collection of test cases stored by this suite."""
