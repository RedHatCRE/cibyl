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

from cibyl.sources.zuul.utils.tests.types import Test


@dataclass
class TempestTest(Test):
    """Representation of a tempest test case.
    """
    class_name: str
    """Full path to the class containing the test case."""
    skip_reason: Optional[str] = None
    """Why the test case was skipped."""
    failure_reason: Optional[str] = None
    """Why the test case failed."""
