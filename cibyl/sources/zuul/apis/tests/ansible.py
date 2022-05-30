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
import logging

from jsonschema.validators import Draft7Validator
from overrides import overrides

from cibyl.sources.zuul.apis.builds import ArtifactKind
from cibyl.sources.zuul.apis.tests import Test, TestFinder, TestSuite
from cibyl.utils.net import download_into_memory

LOG = logging.getLogger(__name__)


class AnsibleTest(Test):
    phase: str
    host: str
    command: str = None
    message: str = None


class AnsibleTestParser:
    DEFAULT_TEST_SCHEMA = \
        'data/json/schemas/zuul/ansible_test.json'

    def __init__(self, test_schema=DEFAULT_TEST_SCHEMA):
        self._test_schema = test_schema

    def parse(self, data):
        """

        :param data:
        :type data: dict[str, Any]
        :return:
        :rtype: :class:`AnsibleTest`
        """
        pass


class AnsibleTestFinder(TestFinder):
    DEFAULT_MANIFEST_SCHEMA = \
        'data/json/schemas/zuul/manifest.json'

    DEFAULT_FILES_OF_INTEREST = (
        'job-output.json'
    )

    def __init__(self,
                 parser=AnsibleTestParser(),
                 manifest_validator=Draft7Validator(DEFAULT_MANIFEST_SCHEMA),
                 files_of_interest=DEFAULT_FILES_OF_INTEREST):
        self._parser = parser
        self._manifest_validator = manifest_validator
        self._files_of_interest = files_of_interest

    @overrides
    def find(self, build):
        def get_manifests():
            return [
                artifact.url
                for artifact in build.artifacts
                if artifact.kind == ArtifactKind.ZUUL_MANIFEST
            ]

        result = []
        session = build.session.session

        for manifest in get_manifests():
            contents = json.loads(
                download_into_memory(manifest, session=session)
            )

            if self._manifest_validator.is_valid(contents):
                msg = "Unknown format for manifest in: '%s'. Ignoring..."
                LOG.warning(msg, manifest)
                continue

            for file_def in contents['tree']:
                if 'name' not in file_def:
                    LOG.info("Got build's log file with no name. Ignoring...")
                    continue

                file_name = file_def['name']

                if file_name in self._files_of_interest:
                    LOG.info(f"Parsing tests from file: '{file_name}'...")
                    result.append(
                        self._parse_tests(
                            json.loads(
                                download_into_memory(
                                    f"{build.log_url}{file_name}",
                                    session=session
                                )
                            )
                        )
                    )

        return result

    def _parse_tests(self, json):
        """

        :param json:
        :type json: dict
        :return:
        :rtype: list[:class:`cibyl.sources.zuul.apis.tests.TestSuite`]
        """
        tests = []

        for test in json:
            pass
