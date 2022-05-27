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
from cibyl.utils.strings import IndentedTextBuilder
from cibyl.utils.time import as_minutes


def has_status_section(build):
    """Checks whether a build has enough data to build a status entry for
    its description.

    :param build: The build to check.
    :type build: :class:`cibyl.models.ci.base.build.Build`
    :return: True if a status section can be built, False if not.
    :rtype: bool
    """
    return build.status.value


def get_status_section(palette, build):
    """Generates the text describing the status of a build.

    :param palette: The palette of colors to follow.
    :type palette: :class:`cibyl.utils.colors.ColorPalette`
    :param build: The build to get the data from.
    :type build: :class:`cibyl.models.ci.base.build.Build`
    :return: The text with the status of the build.
    :rtype: str
    """
    if not has_status_section(build):
        raise ValueError('Build has no status to create a section for.')

    text = IndentedTextBuilder()

    status_x_color_map = {
        'SUCCESS': lambda: palette.green(build.status.value),
        'FAILURE': lambda: palette.red(build.status.value),
        'FAILED': lambda: palette.red(build.status.value),
        'NOT EXECUTED': lambda: palette.blue(build.status.value),
        'UNSTABLE': lambda: palette.yellow(build.status.value)
    }

    status = status_x_color_map.get(
        build.status.value,
        lambda: palette.underline(build.status.value)
    )()

    text.add(palette.blue('Status: '), 0)
    text[-1].append(status)

    return text.build()


def has_duration_section(build):
    """Checks whether a build has enough data to build a duration entry for
    its description.

    :param build: The build to check.
    :type build: :class:`cibyl.models.ci.base.build.Build`
    :return: True if a duration section can be built, False if not.
    :rtype: bool
    """
    return build.duration.value


def get_duration_section(palette, build):
    """Generates the text describing the duration of a build.

    :param palette: The palette of colors to follow.
    :type palette: :class:`cibyl.utils.colors.ColorPalette`
    :param build: The build to get the data from.
    :type build: :class:`cibyl.models.ci.base.build.Build`
    :return: The text with the duration of the build.
    :rtype: str
    """
    if not has_duration_section(build):
        raise ValueError('Build has no duration to create a section for.')

    text = IndentedTextBuilder()

    text.add(palette.blue('Duration: '), 0)
    text[-1].append(f'{as_minutes(build.duration.value):.4f}min')

    return text.build()
