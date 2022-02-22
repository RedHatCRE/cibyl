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

from cibyl.orchestrator import Orchestrator


class TestOrchestrator(TestCase):
    """Testing Orchestrator class"""

    def setUp(self):
        self.orchestrator = Orchestrator()

    def test_orchestrator_config(self):
        """Testing Orchestartor config attribute and method"""
        self.assertTrue(hasattr(self.orchestrator, 'config'))
        self.assertEqual(self.orchestrator.load_configuration(), None)

    def test_orchestrator_query(self):
        """Testing Orchestartor query method"""
        self.assertEqual(self.orchestrator.run_query(), None)
