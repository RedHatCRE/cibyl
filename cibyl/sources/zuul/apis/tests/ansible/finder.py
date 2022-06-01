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
from typing import Iterable

from overrides import overrides

from cibyl.sources.zuul.apis.builds import ArtifactKind
from cibyl.sources.zuul.apis.tests.ansible.parser import AnsibleTestParser
from cibyl.sources.zuul.apis.tests.finder import TestFinder
from cibyl.utils.json import Draft7ValidatorFactory, JSONValidatorFactory
from cibyl.utils.net import download_into_memory

LOG = logging.getLogger(__name__)


class AnsibleTestFinder(TestFinder):
    class TestArgs:
        DEFAULT_FILES_OF_INTEREST = ['job-output.json']

        parser: AnsibleTestParser = AnsibleTestParser()
        files_of_interest: Iterable[str] = DEFAULT_FILES_OF_INTEREST

    class ManifestArgs:
        DEFAULT_MANIFEST_SCHEMA = 'data/json/schemas/zuul/manifest.json'

        schema: str = DEFAULT_MANIFEST_SCHEMA
        validator_factory: JSONValidatorFactory = Draft7ValidatorFactory()

    def __init__(self, manifest_args=ManifestArgs(), test_args=TestArgs()):
        """

        :param manifest_args:
        :type manifest_args: :class:`AnsibleTestFinder.ManifestArgs`
        :param test_args:
        :type test_args: :class:`AnsibleTestFinder.TestArgs`
        """
        self._parser = test_args.parser
        self._files_of_interest = test_args.files_of_interest

        self._manifest_schema = manifest_args.schema
        self._manifest_validator_factory = manifest_args.validator_factory

    @staticmethod
    def _download_json(session, url):
        return json.loads(download_into_memory(url, session=session))

    @staticmethod
    def _get_build_session(build):
        return build.session.session

    @staticmethod
    def _get_build_manifests(build):
        return [
            artifact.url
            for artifact in build.artifacts
            if artifact.kind == ArtifactKind.ZUUL_MANIFEST
        ]

    @staticmethod
    def _get_log_file_url(build, file):
        return f"{build.log_url}{file}"

    @overrides
    def find(self, build):
        result = []

        for manifest in self._get_build_manifests(build):
            result += self._parse_manifest(build, manifest)

        return result

    def _parse_manifest(self, build, manifest):
        result = []

        session = self._get_build_session(build)
        validator = self._new_manifest_validator()

        contents = self._download_json(session, manifest)

        if not validator.is_valid(contents):
            msg = "Unknown format for manifest in: '%s'. Ignoring..."
            LOG.warning(msg, manifest)
            return result

        for file in contents['tree']:
            name = file['name']

            if name in self._files_of_interest:
                LOG.info(f"Parsing tests from file: '{name}'...")
                result += self._parse_tests(
                    build,
                    self._get_log_file_url(build, name)
                )

        return result

    def _new_manifest_validator(self):
        return self._manifest_validator_factory.from_file(
            self._manifest_schema
        )

    def _parse_tests(self, build, test):
        result = []

        try:
            result += self._parser.parse(
                self._download_json(
                    self._get_build_session(build), test
                )
            )
        except ValueError as ex:
            LOG.warning(
                "Failed to fetch tests from: '%s'. Reason: '%s'.",
                test, str(ex)
            )

        return result
