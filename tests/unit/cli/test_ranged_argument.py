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

from cibyl.cli.ranged_argument import (EXPRESSION_PATTERN, RANGE_OPERATORS,
                                       VALID_OPS, Range)


def is_valid_regex(match_obj, operator, operand):
    """Check that a string is matched correctly by the regex."""
    operator_str = match_obj.group(1)
    operand_str = match_obj.group(2)
    return operand_str == operand and operator == operator_str


class TestRange(TestCase):
    """Test helper module for ranged Arguments."""

    def test_regex(self):
        """Check that the range regex works as intended."""
        self.assertIsNone(EXPRESSION_PATTERN.search("abcd"))
        matched_str = EXPRESSION_PATTERN.search(">>4")
        self.assertTrue(is_valid_regex(matched_str, ">>", "4"))
        matched_str = EXPRESSION_PATTERN.search("!=4")
        self.assertTrue(is_valid_regex(matched_str, "!=", "4"))
        matched_str = EXPRESSION_PATTERN.search("<=45")
        self.assertTrue(is_valid_regex(matched_str, "<=", "45"))

    def test_Range(self):
        """Test that Range namedtuple works as intended."""
        range1 = Range(">", "2")
        range2 = Range("<", "2")
        self.assertEqual(range1.operator, ">")
        self.assertEqual(range1.operand, "2")
        self.assertEqual(range2.operator, "<")
        self.assertEqual(range2.operand, "2")
        self.assertNotEqual(range1, range2)

    def test_range_operators(self):
        """Test that range operator dictionary works as intended."""
        self.assertTrue(RANGE_OPERATORS["<"](2, 3))
        self.assertTrue(RANGE_OPERATORS[">"](5, 3))
        self.assertTrue(RANGE_OPERATORS[">="](3, 3))
        self.assertTrue(RANGE_OPERATORS["<="](3, 3))
        self.assertTrue(RANGE_OPERATORS["=="](3, 3))
        self.assertTrue(RANGE_OPERATORS["="](3, 3))
        self.assertTrue(RANGE_OPERATORS["!="](2, 3))

    def test_valid_operators_str(self):
        """Test that VALID_OPS string contains all supported operators."""
        for op in RANGE_OPERATORS:
            self.assertIn(op, VALID_OPS)
