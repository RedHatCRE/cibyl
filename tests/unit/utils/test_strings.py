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

from cibyl.utils.strings import IndentedTextBuilder


class TestIndentedTextBuilder(TestCase):
    """Tests for :class:`IndentedTextBuilder`.
    """

    def test_add_multiple_levels(self):
        """Checks that the text is indented.
        """
        builder = IndentedTextBuilder()

        builder \
            .add('Header', 0) \
            .add('Section', 1) \
            .add('Paragraph', 2)

        expected = 'Header\n  Section\n    Paragraph'

        self.assertEqual(expected, builder.build())

    def test_can_modify_line(self):
        """Checks that a line on the builder can be modified individually.
        """
        builder = IndentedTextBuilder()

        builder.add('Text1,', 0)
        builder[0].append('Text2')

        expected = 'Text1,Text2'

        self.assertEqual(expected, builder.build())

    def test_nested_builders(self):
        """Checks that the result of builder conserves indentation when
        added to another.
        """
        builder1 = IndentedTextBuilder()
        builder2 = IndentedTextBuilder()

        builder1.add('Header', 0)
        builder1.add('Section', 1)

        builder2.add('Paragraph 1', 0)
        builder2.add('List 1', 1)

        builder1.add(builder2.build(), 2)

        expected = 'Header\n  Section\n    Paragraph 1\n      List 1'

        self.assertEqual(expected, builder1.build())

    def test_append_non_string(self):
        """Checks that other data types other than str can be appended to
        lines.
        """
        builder = IndentedTextBuilder()

        builder.add('Line ', 0)
        builder[-1].append(1)

        expected = 'Line 1'

        self.assertEqual(expected, builder.build())
