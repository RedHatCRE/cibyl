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
from cibyl.utils.colors import ColorPalette


def get_status_colored(palette: ColorPalette, status: str) -> str:
    """Generates the text describing the status of a build.

    :param palette: The palette of colors to follow.
    :param status: The status to color.
    :return: The text with the status colored.
    """

    status_x_color_map = {
            'SUCCESS': lambda: palette.green(status),
            'FAILURE': lambda: palette.red(status),
            'FAILED': lambda: palette.red(status),
            'NOT_EXECUTED': lambda: palette.blue(status),
            'UNSTABLE': lambda: palette.yellow(status)
    }

    return status_x_color_map.get(status, lambda: palette.underline(status))()
