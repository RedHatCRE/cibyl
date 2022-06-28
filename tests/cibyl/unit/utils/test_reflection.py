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
import importlib.util
from unittest import TestCase
from unittest.mock import Mock

import cibyl.utils.files
from cibyl.utils.reflection import get_classes_in, load_module


class TestLoadModule(TestCase):
    def test_three_steps_are_made(self):
        """Checks that the three-step process to load a module is performed.
        """
        spec = Mock()
        spec.loader.exec_module = Mock()

        module = Mock()

        name = 'module'
        path = 'some/path'

        cibyl.utils.reflection.get_file_name_from_path = Mock()
        cibyl.utils.reflection.get_file_name_from_path.return_value = name

        importlib.util.spec_from_file_location = Mock()
        importlib.util.spec_from_file_location.return_value = spec

        importlib.util.module_from_spec = Mock()
        importlib.util.module_from_spec.return_value = module

        result = load_module(path)

        self.assertEqual(module, result)

        cibyl.utils.reflection.get_file_name_from_path.assert_called_once_with(
            path
        )

        importlib.util.spec_from_file_location.assert_called_once_with(
            name, path
        )

        importlib.util.module_from_spec.assert_called_once_with(
            spec
        )

        spec.loader.exec_module.assert_called_once_with(
            module
        )


class TestGetClassesIn(TestCase):
    """Tests for :func:`get_classes_in`.
    """

    class TestClass:
        """Used as a sample for a class symbol.
        """

    @staticmethod
    def test_function():
        """Used a sample for a function symbol.
        """

    def test_gets_classes_in_module(self):
        """Checks that the function lists the class symbols found on the
        given module.
        """
        module = Mock()
        module.cls = TestGetClassesIn.TestClass
        module.func = TestGetClassesIn.test_function

        result = get_classes_in(module)

        self.assertEqual([TestGetClassesIn.TestClass], result)
