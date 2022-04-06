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
from enum import Enum


class OutputStyle(Enum):
    TEXT = 0
    COLORIZED = 1

    @staticmethod
    def from_str(label):
        if label == 'text':
            return OutputStyle.TEXT
        elif label == 'colorized':
            return OutputStyle.COLORIZED
        else:
            raise NotImplementedError(f'Unknown format: {label}')
