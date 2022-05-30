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
import logging
from typing import Dict

from cibyl.sources.zuul.apis.builds import ArtifactKind
from cibyl.sources.zuul.apis.tests import TestFinder, Test
from cibyl.utils.net import download_into_memory

LOG = logging.getLogger(__name__)


class AnsibleTest(Test):
    phase: str
    host: str
    command: str = None
    message: str = None


class AnsibleTestParser:
    def parse(self, data):
        """

        :param data:
        :type data: Dict[str, Any]
        :return:
        :rtype: :class:`AnsibleTest`
        """
        pass


class AnsibleTestFinder(TestFinder):
    DEFAULT_FILES_OF_INTEREST = (
        'job-output.json'
    )

    def __init__(self, parser=AnsibleTestParser()):
        self._parser = parser

    def find(self, build, test_def_files=DEFAULT_FILES_OF_INTEREST):
        def get_manifests():
            return [
                artifact
                for artifact in build.artifacts
                if artifact.kind == ArtifactKind.ZUUL_MANIFEST
            ]

        result = []

        for manifest in get_manifests():
            contents = download_into_memory(manifest.url)

            if 'tree' not in contents:
                msg = "Unknown format for manifest in: '%s'. Ignoring..."
                LOG.warning(msg, manifest.url)
                continue

            for file in manifest['tree']:
                if file.get('name') in test_def_files:
                    pass

        return result
