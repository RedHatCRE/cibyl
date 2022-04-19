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
from cibyl.models.ci.printers import PrintMode
from cibyl.models.ci.printers.colored import ColoredPrinter, ColorPalette


class ClearText(ColorPalette):
    def red(self, text):
        return text

    def green(self, text):
        return text

    def blue(self, text):
        return text

    def yellow(self, text):
        return text

    def underline(self, text):
        return text


class RawPrinter(ColoredPrinter):
    def __init__(self, mode=PrintMode.COMPLETE, verbosity=0):
        super().__init__(mode, verbosity, ClearText())
