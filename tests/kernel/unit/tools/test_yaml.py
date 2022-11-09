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
from unittest.mock import Mock

from kernel.tools.yaml import YAMLError, YAMLFile


class TestYAMLFile(TestCase):
    """Tests for :class:`YAMLFile`.
    """

    def test_nothing_on_no_schema(self):
        """Checks that is no schema is provided, the data is consumed without
        question.
        """
        file = Mock()

        tools = Mock()
        tools.validators = Mock()
        tools.validators.from_file = Mock()

        YAMLFile(
            file=file,
            schema=None,
            tools=tools
        )

        tools.validators.from_file.assert_not_called()

    def test_schema_unsatisfied(self):
        """Checks that an error is thrown if the schema is not satisfied.
        """
        raw = 'hello: world'
        yaml = {'hello': 'world'}

        file = Mock()
        file.read = Mock()
        file.read.return_value = raw

        schema = Mock()

        validator = Mock()
        validator.is_valid = Mock()
        validator.is_valid.return_value = False

        parser = Mock()
        parser.as_yaml = Mock()
        parser.as_yaml.return_value = yaml

        tools = Mock()
        tools.parser = parser
        tools.validators = Mock()
        tools.validators.from_file = Mock()
        tools.validators.from_file.return_value = validator

        with self.assertRaises(YAMLError):
            YAMLFile(
                file=file,
                schema=schema,
                tools=tools
            )

        tools.validators.from_file.assert_called_with(schema)

        file.read.assert_called()
        parser.as_yaml.assert_called_with(raw)

        validator.is_valid.assert_called_with(yaml)

    def test_schema_satisfied(self):
        """Checks that the object is created if the data satisfies the given
        schema.
        """
        raw = 'hello: world'
        yaml = {'hello': 'world'}

        file = Mock()
        file.read = Mock()
        file.read.return_value = raw

        schema = Mock()

        validator = Mock()
        validator.is_valid = Mock()
        validator.is_valid.return_value = True

        parser = Mock()
        parser.as_yaml = Mock()
        parser.as_yaml.return_value = yaml

        tools = Mock()
        tools.parser = parser
        tools.validators = Mock()
        tools.validators.from_file = Mock()
        tools.validators.from_file.return_value = validator

        result = YAMLFile(
            file=file,
            schema=schema,
            tools=tools
        )

        self.assertEqual(yaml, result.data)

        tools.validators.from_file.assert_called_with(schema)

        file.read.assert_called()
        parser.as_yaml.assert_called_with(raw)

        validator.is_valid.assert_called_with(yaml)
