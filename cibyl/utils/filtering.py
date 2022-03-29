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
import re
from typing import Dict, Pattern

from cibyl.cli.argument import Argument


def satisfy_regex_match(model: Dict[str, str], pattern: Pattern,
                        field_to_check: str):
    """Check whether model (job or build) should be included according to
    the user input.
    The model should be added if the information provided field_to_check
    (the model name or url for example) is matches the regex pattern.

    :param model: model information obtained from jenkins
    :type model: str
    :param pattern: regex patter that the model name should match
    :type pattern: :class:`re.Pattern`
    :param field_to_check: model field to perform the check
    :param field_to_check: str
    :returns: Whether the model satisfies user input
    :rtype: bool
    """
    return re.search(pattern, model[field_to_check]) is not None


def satisfy_exact_match(model: Dict[str, str], user_input: Argument,
                        field_to_check: str):
    """Check whether model should be included according to the user input. The
    model should be added if the information provided field_to_check
    (the model name or url for example) is present in the user_input values.

    :param model: model information obtained from jenkins
    :type model: str
    :param user_input: input argument specified by the user
    :type model_urls: :class:`.Argument`
    :param field_to_check: Job field to perform the check
    :param field_to_check: str
    :returns: Whether the model satisfies user input
    :rtype: bool
    """
    return model[field_to_check] in user_input.value


def satisfy_case_insensitive_match(model: Dict[str, str], user_input: Argument,
                                   field_to_check: str):
    """Check whether model should be included according to the user input. The
    model should be added if the information provided field_to_check
    (the model name or url for example) is an exact case-insensitive match to
    the information in the user_input values.

    :param model: model information obtained from jenkins
    :type model: str
    :param user_input: input argument specified by the user
    :type model_urls: :class:`.Argument`
    :param field_to_check: Job field to perform the check
    :param field_to_check: str
    :returns: Whether the model satisfies user input
    :rtype: bool
    """
    lowercase_input = [status.lower() for status in user_input.value]
    return model[field_to_check].lower() in lowercase_input


def apply_filters(iterable, *filters):
    """Applies a set of filters to a collection.

    :param iterable: The collection to filter.
    :param filters: List of filters to apply.
    :return: The collection post-filtering.
    :rtype: list
    """
    result = list(iterable)

    for check in filters:
        result = list(filter(check, result))

    return result
