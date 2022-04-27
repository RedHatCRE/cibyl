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
from unittest import TestCase

from cibyl.models.ci.system import (BASE_SYSTEM_API, JOBS_SYSTEM_API,
                                    ZUUL_SYSTEM_API, System)
from cibyl.models.ci.system_factory import SystemFactory, SystemType


class TestAPI(TestCase):
    def test_aggregated_system_api(self):
        """Checks that the creation of multiple types of systems leads to
        the combined API of all of them.
        """
        SystemFactory.create_system(SystemType.JENKINS, 'Jenkins')
        SystemFactory.create_system(SystemType.ZUUL, 'Zuul')

        # Check subsets that form the System API
        self.assertEqual(System.API, {**System.API, **BASE_SYSTEM_API})
        self.assertEqual(System.API, {**System.API, **JOBS_SYSTEM_API})
        self.assertEqual(System.API, {**System.API, **ZUUL_SYSTEM_API})
