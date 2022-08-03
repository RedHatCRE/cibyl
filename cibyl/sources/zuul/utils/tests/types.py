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
from enum import StrEnum
from typing import Generic, Optional, TypeVar, Iterable

from dataclasses import dataclass, field


class TestResult(StrEnum):
    UNKNOWN = 'UNKNOWN'
    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'
    SKIPPED = 'SKIPPED'


@dataclass
class Test(ABC):
    name: str
    result: TestResult
    duration: float
    url: str


T = TypeVar("T", bound=Test)


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
