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
from tempfile import TemporaryDirectory
from unittest import TestCase

from tripleo.utils.git.gitpython import GitPython
from tripleo.utils.types import URL, Dir


class TestGitPython(TestCase):
    """Tests for :class:'GitPython'.
    """

    def test_get_as_text(self):
        """Checks that it is possible to get the contents of a file in the
        repository as text.
        """
        file = 'README.rst'
        cibyl = URL('https://github.com/rhos-infra/cibyl.git')

        with open(file, 'r') as target:
            with TemporaryDirectory() as folder:
                git = GitPython()
                directory = Dir(folder)

                with git.clone(cibyl, directory) as repo:
                    self.assertEqual(target.read(), repo.get_as_text(file))
