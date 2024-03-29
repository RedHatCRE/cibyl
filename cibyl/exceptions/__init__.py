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


class CibylException(Exception):
    """Parent class for all cibyl exceptions for easier control of the
    exceptions' representation.
    """

    def __init__(self, message=''):
        """Constructor.

        :param message: The reason for this error.
        :type message: str
        """
        self.message = message
        super().__init__(*[message])
