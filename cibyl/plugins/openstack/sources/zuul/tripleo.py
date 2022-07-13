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


class QuickStartFileCreator:
    """Utility that helps to produce the name of files stored under the
    QuickStart repository.
    """
    DEFAULT_FEATURESET_TEMPLATE = Template('featureset$number.yml')
    """Default template used to generate the name of featureset files."""
    DEFAULT_NODES_TEMPLATE = Template('$topology.yml')
    """Default template used to generate the name of nodes files."""
    DEFAULT_RELEASE_TEMPLATE = Template('$name.yml')
    """Default template used to generate the name of release files."""

    def __init__(
        self,
        featureset_template: Template = DEFAULT_FEATURESET_TEMPLATE,
        nodes_template: Template = DEFAULT_NODES_TEMPLATE,
        release_template: Template = DEFAULT_RELEASE_TEMPLATE
    ):
        """Constructor.

        :param featureset_template: Template that will be used to generate
            the name of featureset files. The template only takes one argument,
            $number, which is the ID of the featureset.
        :param nodes_template: Template that will be used to generate the
            name of nodes files. The template only takes one argument,
            $topology, which is the name of the file without its extension.
        :param release_template: Template that will be used to generate the
            name of release files. The template only takes one argument,
            $name, which is the name of the release ('wallaby').
        """
        self._featureset_template = featureset_template
        self._nodes_template = nodes_template
        self._release_template = release_template

    @property
    def featureset_template(self) -> Template:
        """
        :return: Template of featureset files.
        """
        return self._featureset_template

    @property
    def nodes_template(self):
        """
        :return: Template for node files.
        """
        return self._nodes_template

    @property
    def release_template(self):
        """
        :return: Template for release files.
        """
        return self._release_template

    def create_featureset(self, number: str) -> str:
        """Generate a new featureset file name from the given parameters.

        :param number: ID of the featureset. For example: '052'.
        :return: Full name of the file inside the QuickStart repository that
            defines the featureset.
        """
        return self.featureset_template.substitute(number=number)

    def create_nodes(self, topology: str) -> str:
        """Generate a new nodes file name from the given parameters.

        :param topology: Topology that leads to one of the nodes file on the
            QuickStart repository. For example: '1ctlr'.
        :return: Full name of the file inside the QuickStart repository that
            defines the topology.
        """
        return self.nodes_template.substitute(topology=topology)

    def create_release(self, name: str) -> str:
        """Generate a new release file name from the given parameters.

        :param name: Name of the release. For example: 'wallaby'.
        :return: Full name of the file inside the QuickStart repository that
            defines the release.
        """
        return self.release_template.substitute(name=name)


class QuickStartPathCreator:
    """Utility defined to ease the creation of paths inside the QuickStart
    repository.
    """
    DEFAULT_PATH_TEMPLATE = Template('config/$folder/$file')
    """Default template used to generate paths inside the repository."""

    DEFAULT_ENVIRONMENT_FOLDER = 'environments'
    """Default folder containing environments."""
    DEFAULT_FEATURESET_FOLDER = 'general_config'
    """Default folder containing featuresets."""
    DEFAULT_NODES_FOLDER = 'nodes'
    """Default folder containing topologies."""
    DEFAULT_RELEASE_FOLDER = 'release'
    """Default folder containing releases."""

    def __init__(self, path_template: Template = DEFAULT_PATH_TEMPLATE):
        """Constructor.

        :param path_template: Template this will use to generate paths
            within the QuickStart repository. The template takes two
            arguments: $folder and $file. $folder can be the directory where
            interesting files are stored. $file is the full name of a file
            inside the directory given by $folder.
        """
        self._path_template = path_template

    @property
    def path_template(self) -> Template:
        """
        :return: Template this uses to generate paths inside the repository.
        """
        return self._path_template

    def create_generic_path(self, folder: str, file: str) -> str:
        """Create a generic path within the repository.

        :param folder: Directory where the file is located.
        :param file: File within the directory to point to. Can be left
            blank to just get the directory.
        :return: The generated path.
        """
        return self.path_template.substitute(folder=folder, file=file)

    def create_environment_path(self, file: str) -> str:
        """Creates a path pointing to an environments file.

        :param file: File within the directory.
        :return: The generated path.
        """
        return self.create_generic_path(
            folder=QuickStartPathCreator.DEFAULT_ENVIRONMENT_FOLDER,
            file=file
        )

    def create_featureset_path(self, file: str) -> str:
        """Creates a path pointing to a featureset file.

        :param file: File within the directory.
        :return: The generated path.
        """
        return self.create_generic_path(
            folder=QuickStartPathCreator.DEFAULT_FEATURESET_FOLDER,
            file=file
        )

    def create_nodes_path(self, file: str) -> str:
        """Creates a path pointing to a topology file.

        :param file: File within the directory.
        :return: The generated path.
        """
        return self.create_generic_path(
            folder=QuickStartPathCreator.DEFAULT_NODES_FOLDER,
            file=file
        )

    def create_release_path(self, file: str) -> str:
        """Creates a path pointing to a release file.

        :param file: File within the directory.
        :return: The generated path.
        """
        return self.create_generic_path(
            folder=QuickStartPathCreator.DEFAULT_RELEASE_FOLDER,
            file=file
        )
