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
from tripleo.insights.io import DeploymentOutline, DeploymentSummary
from tripleo.insights.validation import OutlineValidator


class DeploymentLookUp:
    def __init__(self, validator: OutlineValidator = OutlineValidator()):
        self._validator = validator

    @property
    def validator(self):
        return self._validator

    def run(self, outline: DeploymentOutline) -> DeploymentSummary:
        self._validate_outline(outline)

    def _validate_outline(self, outline: DeploymentOutline) -> None:
        is_valid, error = self.validator.validate(outline)

        if not is_valid:
            raise error
