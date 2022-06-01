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
from cibyl.outputs.cli.ci.system.common.status import get_status_colored
from cibyl.utils.strings import IndentedTextBuilder
from cibyl.utils.time import as_minutes


def print_stage(stage, palette, verbosity=0):
    """
        Generate string representation of a Stage model.

        :param test: The stage.
        :type test: :class:`cibyl.models.ci.base.stage.Stage`
        :param palette: The palette of colors to follow.
        :type palette: :class:`cibyl.utils.colors.ColorPalette`
        :param verbosity: The verbosity level to use.
        :type verbosity: int
        :return: Textual representation of the provided model.
        :rtype: str
    """
    printer = IndentedTextBuilder()

    printer.add(palette.blue('- '), 0)
    printer[-1].append(stage.name.value)

    if verbosity > 0:
        if stage.status.value:
            printer.add(palette.blue('Status: '), 1)
            printer[-1].append(get_status_colored(palette, stage.status.value))

        if stage.duration.value:
            printer.add(palette.blue('Duration: '), 1)
            printer[-1].append(f'{as_minutes(stage.duration.value):.4f}min')
    return printer.build()
