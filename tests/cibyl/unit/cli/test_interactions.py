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
import builtins
from unittest import TestCase
from unittest.mock import Mock

from cibyl.cli.interactions import ask_yes_no_question


class TestYesNoQuestion(TestCase):
    """Tests function :func:`cibyl.cli.interactions.ask_yes_no_question`.
    """

    def test_true_on_y(self):
        """Checks that if the user says yes, then it returns true.
        """
        builtins.input = Mock()
        builtins.input.return_value = 'y'

        self.assertTrue(ask_yes_no_question('Question?'))

    def test_false_on_n(self):
        """Checks that if the user says no, then it returns false.
        """
        builtins.input = Mock()
        builtins.input.return_value = 'n'

        self.assertFalse(ask_yes_no_question('Question?'))

    def test_false_on_nothing(self):
        """Checks that if the user says nothing, then it returns false.
        """
        builtins.input = Mock()
        builtins.input.return_value = ''

        self.assertFalse(ask_yes_no_question('Question?'))
