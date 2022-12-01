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

from kernel.tools.json import Draft7Validator, NullValidator, SchemaError


class TestNullValidator(TestCase):
    """Tests for :class:`NullValidator`.
    """

    def test_always_returns_true(self):
        """Checks that the validator will consider all data to be valid.
        """
        validator = NullValidator(schema=Mock())

        self.assertTrue(validator.is_valid({}))
        self.assertTrue(validator.is_valid([{'hello': 'world'}]))
        self.assertTrue(validator.is_valid(Mock()))


class TestDraft7Validator(TestCase):
    """Tests for :class:`Draft7Validator`.
    """

    def test_error_on_invalid_schema(self):
        """Checks that an error is thrown when the schema does not follow
        the draft 7 specification.
        """
        with self.assertRaises(SchemaError):
            Draft7Validator(schema=Mock())

    def test_fails_on_invalid_data(self):
        """Checks that the validator will notice when some data does
        not conform to the schema.
        """
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "$id": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties":
                {
                    "hello": {
                        "type": "string",
                        "const": "world"
                    },
                    "additionalProperties": False
                },
            "additionalProperties": False
        }

        data = {
            'no-hello': '>:['
        }

        validator = Draft7Validator(schema)

        self.assertFalse(validator.is_valid(data))

    def test_pass_on_valid_data(self):
        """Checks that the validator will notice when some data does conform
        to the schema.
        """
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "$id": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties":
                {
                    "hello": {
                        "type": "string",
                        "const": "world"
                    },
                    "additionalProperties": False
                },
            "additionalProperties": False
        }

        data = {
            'hello': 'world'
        }

        validator = Draft7Validator(schema)

        self.assertTrue(validator.is_valid(data))
