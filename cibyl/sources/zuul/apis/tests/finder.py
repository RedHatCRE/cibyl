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
from abc import ABC, abstractmethod


class TestFinder(ABC):
    """Takes care of going through the artifacts of a build and find in there
    the test cases that were run."""

    @abstractmethod
    def find(self, build):
        """Fetches all tests executed by the build, grouped in test suites.

        :param build: The build to get the tests from.
        :type build: :class:`cibyl.sources.zuul.apis.rest.ZuulBuildRESTClient`
        :return: The tests, grouped by suites.
        :rtype: list[:class:`TestSuite`]
        """
        raise NotImplementedError
