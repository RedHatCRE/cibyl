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
from cibyl.models.ci.base.build import Build
from cibyl.outputs.cli.ci.system.common.status import get_status_colored
from cibyl.utils.colors import ColorPalette
from cibyl.utils.strings import IndentedTextBuilder
from cibyl.utils.time import as_minutes


def has_status_section(build: Build) -> bool:
    """Checks whether a build has enough data to build a status entry for
    its description.

    :param build: The build to check.
    :return: True if a status section can be built, False if not.
    """
    return build.status.value


def get_status_section(palette: ColorPalette, build: Build) -> str:
    """Generates the text describing the status of a build.

    :param palette: The palette of colors to follow.
    :param build: The build to get the data from.
    :return: The text with the status of the build.
    """
    if not has_status_section(build):
        raise ValueError('Build has no status to create a section for.')

    text = IndentedTextBuilder()

    text.add(palette.blue('Status: '), 0)
    text[-1].append(get_status_colored(palette, build.status.value))

    return text.build()


def has_duration_section(build: Build) -> bool:
    """Checks whether a build has enough data to build a duration entry for
    its description.

    :param build: The build to check.
    :return: True if a duration section can be built, False if not.
    """
    return build.duration.value


def get_duration_section(palette: ColorPalette, build: Build) -> str:
    """Generates the text describing the duration of a build.

    :param palette: The palette of colors to follow.
    :param build: The build to get the data from.
    :return: The text with the duration of the build.
    """
    if not has_duration_section(build):
        raise ValueError('Build has no duration to create a section for.')

    text = IndentedTextBuilder()

    text.add(palette.blue('Duration: '), 0)
    text[-1].append(f'{as_minutes(build.duration.value):.2f}min')

    return text.build()
