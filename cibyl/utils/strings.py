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
import validators


def is_url(string: str) -> bool:
    """
    :param string: The string to test.
    :return: True if the string follows a URL format, False if not.
    """
    result = validators.url(string)

    if isinstance(result, bool):
        return result

    return False


class IndentedTextBuilder:
    """Easy creation of structured text based on indents.

    This additionally implements:
        * len() -> Number of lines on text.
        * [] -> Access line by index.
    """

    class Line:
        """A line of text.
        """

        def __init__(self, text: str, level: int):
            """Constructor.

            :param text: The text on this line.
            :param level: The indentation level of this line.
            """
            self._text = text
            self._level = level

        def __str__(self):
            return f'(Level {self._level}): {self._text}'

        @property
        def text(self):
            """
            :return: The text present on this line.
            :rtype: str
            """
            return self._text

        @property
        def level(self):
            """
            :return: The indentation level of this line.
            :rtype: int
            """
            return self._level

        def append(self, text: str) -> None:
            """Adds additional text at the end of this line.

            :param text: The text to add.
            """
            self._text += str(text)

    def __init__(self, spaces_per_tab: int = 2):
        """Constructor.

        :param spaces_per_tab: Amount of spaces per indentation level.
        """
        self._lines = []
        self._spaces_per_tab = spaces_per_tab

    def __getitem__(self, index):
        return self._lines[index]

    def __len__(self):
        return len(self._lines)

    def pop(self, index=-1):
        return self._lines.pop(index)

    @property
    def spaces_per_tab(self) -> int:
        """
        :return: Amount of spaces per indentation level.
        """
        return self._spaces_per_tab

    def add(self, text: str, level: int) -> 'IndentedTextBuilder':
        """Adds an additional line of text.

        :param text: The text to add.
        :param level: The indentation level.
        :return: The builder instance.
        """
        self._lines.append(self.Line(text, level))
        return self

    def build(self) -> str:
        """Generates the text stored in the builder.

        :return: The generated piece of text.
        """
        result = ''

        for line in self._lines:
            indentation = line.level * self.spaces_per_tab * ' '

            # Some texts may contain more than one line inside. Those lines
            # must all be indented to keep the structure.
            for chunk in line.text.split('\n'):
                result += f'{indentation}{chunk}\n'

        # Remove excess of symbols
        result = result.strip('\n')

        return result
