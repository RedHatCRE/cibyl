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
    def scenario_template(self):
        """
        :return: Template this will use to generate paths to scenario files
        inside the repository.
        """
        return self._scenario_template

    def create_scenario_path(self, file: str) -> str:
        """Creates a path pointing to a scenario file.

        Examples
        ========
        >>> creator = THTPathCreator()
        ... creator.create_scenario_path('my_file.yaml')
        'ci/environments/my_file.yaml'

        :param file: Name of the file, including extension.
        :return: Path to the file, relative to the repostiory's root.
        """
        return self.scenario_template.substitute(file=file)
