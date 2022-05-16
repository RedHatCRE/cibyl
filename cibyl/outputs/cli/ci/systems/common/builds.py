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


def get_status_section(palette, build):
    text = IndentedTextBuilder()

    status_x_color_map = {
        'SUCCESS': lambda: palette.green(build.status.value),
        'FAILURE': lambda: palette.red(build.status.value),
        'UNSTABLE': lambda: palette.yellow(build.status.value)
    }

    status = status_x_color_map.get(
        build.status.value,
        lambda: palette.underline(build.status.value)
    )()

    text.add(palette.blue('Status: '), 1)
    text[-1].append(status)

    return text.build()


def get_duration_section(palette, build):
    text = IndentedTextBuilder()

    text.add(palette.blue('Duration: '), 1)
    text[-1].append(f'{as_minutes(build.duration.value):.2f}m')

    return text.build()
