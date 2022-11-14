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
from pathlib import Path
from unittest import TestCase

from cibyl.sources.zuuld.backends.git import GitBackend
from cibyl.sources.zuuld.frontends.zuul import GitFrontendFactory
from cibyl.sources.zuuld.specs.git import GitSpec
from kernel.tools.urls import URL


class TestGitFrontendFactory(TestCase):
    """Tests for :class:`GitFrontendFactory`.
    """

    def test_builds_frontend_from_kwargs(self):
        """Checks that it is able to generate a new frontend from some
        keyword arguments.
        """
        url1 = 'http://localhost:8080'
        url2 = 'http://localhost:8081'

        kwargs = {
            'repos': [
                {
                    'url': url1
                },
                {
                    'url': url2
                }
            ]
        }

        factory = GitFrontendFactory.from_kwargs(**kwargs)
        result = factory.new()

        specs = list(result.session.specs)
        backend = result.session.backend

        self.assertEqual(2, len(specs))

        self.assertIn(
            GitSpec(
                remote=URL(url1),
                directory=Path('zuul.d/')
            ),
            specs
        )

        self.assertIn(
            GitSpec(
                remote=URL(url1),
                directory=Path('zuul.d/')
            ),
            specs
        )

        self.assertIsInstance(backend, GitBackend)
