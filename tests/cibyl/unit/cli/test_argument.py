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

from cibyl.cli.argument import Argument
from cibyl.cli.ranged_argument import VALID_OPS, Range
from cibyl.exceptions.cli import InvalidArgument


class TestArgument(TestCase):
    """Test Argument class."""

    def setUp(self):
        self.name = "test"
        self.description = "Test argument"
        self.value = ["value"]
        self.arg_type = str
        self.nargs = 1
        self.argument = Argument(name=self.name, description=self.description,
                                 arg_type=self.arg_type, nargs=self.nargs,
                                 value=self.value)
        self.second_argument = Argument(name=self.name, description="",
                                        arg_type=float, nargs="*",
                                        value=self.value)
        self.ranged_argument = Argument(name=self.name,
                                        description=self.description,
                                        arg_type=self.arg_type, nargs="*",
                                        value=[">4", "!=5"], ranged=True)

    def test_check_attributes(self):
        """Check that attributes are properly set."""
        self.assertEqual(self.argument.name, self.name)
        self.assertEqual(self.argument.description, self.description)
        self.assertEqual(self.argument.value, self.value)
        self.assertEqual(self.argument.arg_type, self.arg_type)
        self.assertEqual(self.argument.nargs, self.nargs)
        self.assertIsNone(self.argument.func)
        self.assertIsNone(self.argument.default)
        self.assertEqual(self.argument.level, 0)
        self.assertFalse(self.argument.populated)
        self.assertFalse(self.argument.ranged)

    def test_str(self):
        """Test __str__ method of Argument."""
        self.assertEqual(str(self.argument), str(self.value))

    def test_eq(self):
        """Test __eq__ method of Argument."""
        self.assertEqual(self.argument, self.second_argument)
        argument_different_name = Argument(name="not-test",
                                           description=self.description,
                                           arg_type=self.arg_type,
                                           nargs=self.nargs,
                                           value=self.value)
        argument_different_value = Argument(name=self.name,
                                            description=self.description,
                                            arg_type=self.arg_type,
                                            nargs=self.nargs,
                                            value=[])
        self.assertNotEqual(self.argument, argument_different_name)
        self.assertNotEqual(self.argument, argument_different_value)

    def test_ranged_expression(self):
        """Test that the ranged value is parsed correctly."""
        ranges = [Range(">", "4"), Range("!=", "5")]
        self.assertEqual(self.ranged_argument.value, ranges)

    def test_not_valid_expression(self):
        """Test that an invalid ranged expression raises an exception."""
        exception_msg = f"Expression 'a' in argument {self.name} is not valid"
        with self.assertRaises(InvalidArgument, msg=exception_msg):
            Argument(name=self.name,
                     description=self.description,
                     arg_type=self.arg_type, nargs="*",
                     value=["a"], ranged=True)

    def test_not_multiple_value(self):
        """Test that argument with one value raises an exception."""
        exception_msg = f"Argument '{self.name}' should accept multiple values"

        with self.assertRaises(InvalidArgument, msg=exception_msg):
            Argument(name=self.name,
                     description=self.description,
                     arg_type=self.arg_type, nargs=1,
                     value="<4", ranged=True)

    def test_unknown_operator(self):
        """Test that an unknown operator raises an exception."""
        exception_msg = f"Operator '<<' in argument {self.name} is not valid."
        exception_msg += f"Valid operators include: {VALID_OPS}"

        with self.assertRaises(InvalidArgument, msg=exception_msg):
            Argument(name=self.name,
                     description=self.description,
                     arg_type=self.arg_type, nargs=1,
                     value=["<<4"], ranged=True)

    def test_implicit_operator(self):
        """Test that omitted operator default to equal."""

        arg = Argument(name=self.name,
                       description=self.description,
                       arg_type=self.arg_type, nargs=1,
                       value=["4"], ranged=True)
        self.assertEqual(arg.value[0].operator, "==")
