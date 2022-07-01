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
from typing import Callable, Iterable, Optional

from tripleo.insights.exceptions import InsightsError, InvalidURL
from tripleo.insights.io import DeploymentOutline
from tripleo.utils.urls import is_git

Outline = DeploymentOutline
Validation = Callable[[Outline], Optional[InsightsError]]
Validations = Iterable[Validation]


def validate_urls(outline: Outline) -> Optional[InsightsError]:
    """Checks that the URLs of the outline follow the expected format.

    :param outline: The outline to test.
    :return: None if the URL are valid, an error if not.
    """
    for url in (outline.quickstart, outline.heat):
        if not is_git(url):
            return InvalidURL(f"URL is not a git repository: '{url}'")

    return None


class OutlineValidator:
    """Performs a series of checks on the deployment's outline in order to
    check that it is usable for the lookup task.
    """
    DEFAULT_VALIDATIONS: Validations = (validate_urls,)
    """Defaults checks applied to an outline."""

    def __init__(self, validations: Validations = DEFAULT_VALIDATIONS):
        """Constructor.

        :param validations: The checks that will be applied to the outline.
        """
        self._validations = validations

    @property
    def validations(self) -> Validations:
        """
        :return: The checks that will be applied to the outline.
        """
        return self._validations

    def validate(self, outline: Outline) -> (bool, Optional[InsightsError]):
        """Performs the testing.

        :param outline: The outline to test.
        :return: (True, None) if outline is valid, (False, Error) if not.
        """
        for validation in self._validations:
            error = validation(outline)

            if error:
                return False, error

        return True, None
