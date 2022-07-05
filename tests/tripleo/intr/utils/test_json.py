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
import json
from json import JSONDecodeError
from tempfile import NamedTemporaryFile
from unittest import TestCase

from jsonschema.exceptions import SchemaError
from jsonschema.validators import Draft7Validator

from tripleo.utils.fs import File
from tripleo.utils.json import Draft7ValidatorFactory


class TestDraft7ValidatorFactory(TestCase):
    """Tests for :class:`Draft7ValidatorFactory`.
    """

    def test_json_error(self):
        """Checks that an error is thrown if the file is not formatted as a
        JSON.
        """
        with NamedTemporaryFile('w') as file:
            file.write('some-text')

            factory = Draft7ValidatorFactory()

            with self.assertRaises(JSONDecodeError):
                factory.from_file(File(file.name))

    def test_schema_error(self):
        """Checks that an error is thrown if the file is a JSON, but not a
        schema.
        """
        data = {
            'type': 'some-type'
        }

        with NamedTemporaryFile(mode='w') as file:
            file.write(json.dumps(data))
            file.flush()

            factory = Draft7ValidatorFactory()

            with self.assertRaises(SchemaError):
                factory.from_file(File(file.name))

    def test_validator_is_build(self):
        """Checks that if all conditions meet, the validator is built.
        """
        data = {
            '$schema': 'some-url',
            'type': 'string'
        }

        with NamedTemporaryFile(mode='w') as file:
            file.write(json.dumps(data))
            file.flush()

            factory = Draft7ValidatorFactory()

            result = factory.from_file(File(file.name))

            self.assertIsInstance(result, Draft7Validator)
            self.assertEqual(result.schema, data)
