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
from abc import ABC
from dataclasses import dataclass, field
from enum import Enum
from typing import Generic, Iterable, Optional, TypeVar


class TestResult(Enum):
    """Ending state of a test case.
    """
    UNKNOWN = 'UNKNOWN'
    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'
    SKIPPED = 'SKIPPED'


@dataclass
class Test(ABC):
    """Representation of a generic test case running on a Zuul job.
    """
    name: str
    """Name of the test case."""
    result: TestResult
    """Describes how the test case ended."""
    duration: float
    """Amount of second it took the test to complete."""
    url: str
    """URL to the location where this test is described."""


T = TypeVar("T", bound=Test)
"""Generic type that extends from Test."""


@dataclass
class TestSuite(Generic[T]):
    """Collection on test cases that have something in common.
    """
    name: str
    """Name of the suite."""
    url: Optional[str] = None
    """Page where to get more information about the tests."""
    tests: Iterable[T] = field(default_factory=list)
    """Collection of test cases stored by this suite."""
