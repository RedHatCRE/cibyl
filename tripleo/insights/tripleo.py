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
from string import Template
from typing import Iterable


class THTBranchCreator:
    """Utility to ease the creation of branch names inside the Heat
    Templates repository.
    """
    DEFAULT_IGNORED_RELEASES = ('master',)
    DEFAULT_RELEASE_TEMPLATE = Template('stable/$release')
    """Default template used to generate the branch assigned to a release."""

    def __init__(
        self,
        ignored_releases: Iterable[str] = DEFAULT_IGNORED_RELEASES,
        release_template: Template = DEFAULT_RELEASE_TEMPLATE
    ):
        """Constructor.

        :param ignored_releases: Collection of release names that map 1-to-1
            to their branch and thus need no processing. If one of this is
            seen, then it will be returned as is.
        :param release_template: Template used to generate branch names from
            a RHOS release name. It only takes one argument, $release,
            which is the name of the RHOS release.
        """
        self._ignored_releases = ignored_releases
        self._release_template = release_template

    @property
    def ignored_releases(self) -> Iterable[str]:
        """
        :return: The releases that require no processing to be mapped to
            their branch.
        """
        return self._ignored_releases

    @property
    def release_template(self) -> Template:
        """
        :return: Template used to generate branch names from a RHOS release
            name.
        """
        return self._release_template

    def create_release_branch(self, release: str) -> str:
        """Creates the name of the branch for the given release.

        Examples
        --------
        >>> creator = THTBranchCreator()
        ... creator.create_release_branch('wallaby')
        'stable/wallaby'
        >>> creator = THTBranchCreator(ignored_releases=('master',))
        ... creator.create_release_branch('master')
        'master'

        :param release: Name of the RHOS release. For example: 'wallaby'.
        :return: The branch assigned to that release.
        """
        if release in self.ignored_releases:
            return release

        return self.release_template.substitute(release=release)


class THTPathCreator:
    """Utility to ease the creation of paths inside the Heat Templates
    repository.
    """
    DEFAULT_SCENARIO_PATH_TEMPLATE = Template('ci/environments/$file')
    """Default template used to generate paths to scenario files."""

    def __init__(
        self,
        scenario_template: Template = DEFAULT_SCENARIO_PATH_TEMPLATE
    ):
        """
        :param scenario_template: Template this will use to generate paths
        to scenario files inside the repository. It only takes one argument,
        $file, which is the full name of the scenario file, including
        extension.
        """
        self._scenario_template = scenario_template

    @property
    def scenario_template(self) -> Template:
        """
        :return: Template this will use to generate paths to scenario files
        inside the repository.
        """
        return self._scenario_template

    def create_scenario_path(self, file: str) -> str:
        """Creates a path pointing to a scenario file.

        Examples
        --------
        >>> creator = THTPathCreator()
        ... creator.create_scenario_path('my_file.yaml')
        'ci/environments/my_file.yaml'

        :param file: Name of the file, including extension.
        :return: Path to the file, relative to the repostiory's root.
        """
        return self.scenario_template.substitute(file=file)
