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

from cibyl.utils.colors import Colors

class NonSupportedModelType(Exception):
    """Exception for trying to populate non-supported model"""

    def __init__(self, model_type):
        self.model_type = model_type
        self.message = Colors.red(
        f"""Not supported type for model: {self.model_type}.
            Unable to populate system with pulled data""")
        super().__init__(self.message)


class NoValidEnvironment(Exception):
    """Exception for a case when no valid environment is found."""

    def __init__(self):
        self.message = Colors.red("""No valid environment defined.
 Please ensure the specified environments with --env-name argument
are present in the configuration.
""")
        super().__init__(self.message)


class NoValidSystem(Exception):
    """Exception for a case when no valid system is found."""

    def __init__(self):
        self.message = Colors.red("""No valid system defined.
 Please ensure the specified environments with --systems, --system-name or
 --system-type arguments are present in the configuration.
""")
        super().__init__(self.message)
