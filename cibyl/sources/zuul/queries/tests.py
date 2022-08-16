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
from typing import Iterable

from cibyl.sources.zuul.transactions import BuildResponse as Build
from cibyl.sources.zuul.transactions import TestResponse as Test


def perform_tests_query(build: Build, **kwargs) -> Iterable[Test]:
    """Query for tests.

    :param build: API to interact with the owner of the tests.
    :param kwargs: Arguments coming from the CLI.
    :return: Collection of retrieved tests.
    """
    tests = build.tests()

    # Apply test filters
    if 'tests' in kwargs:
        targets = kwargs['tests'].value

        # An empty '--tests' means all of them
        if targets:
            tests.with_name(*targets)

    if 'test_result' in kwargs:
        tests.with_status(*kwargs['test_result'].value)

    if 'test_duration' in kwargs:
        tests.with_duration(*kwargs['test_duration'].value)

    return tests.get()
