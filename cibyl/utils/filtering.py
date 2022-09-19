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
import sre_constants
from typing import Callable, Dict, Iterable, List, Optional, Pattern

from cibyl.cli.argument import Argument
from cibyl.cli.ranged_argument import RANGE_OPERATORS

IP_PATTERN = re.compile("ipv(.)")
RELEASE_PATTERN = re.compile(r"\d\d\.?\d?")
RELEASE_RUN = re.compile(rf"--version ({RELEASE_PATTERN})")
RELEASE_VERSION = re.compile(rf"PRODUCT_VERSION:({RELEASE_PATTERN})")
TOPOLOGY_PATTERN = re.compile(r"[\_\-]((\d([a-zA-Z])+_?)+)")
PROPERTY_PATTERN = re.compile(r"=(.*)")
NETWORK_BACKEND_PATTERN = re.compile("geneve|gre|vlan|vxlan")
CINDER_BACKEND_PATTERN_STR = "ceph|lvm|netapp-iscsi|netapp-nfs|swift|nfs"
CINDER_BACKEND_PATTERN = re.compile(CINDER_BACKEND_PATTERN_STR)
DEPLOYMENT_PATTERN = re.compile("ovb|baremetal")
OPTIONS = re.compile("yes|no|true|false")
DVR_PATTERN_RUN = re.compile(rf"--network-dvr ({OPTIONS.pattern})")
DVR_PATTERN_NAME = re.compile(r"(non*_)*dvr")
TLS_PATTERN_RUN = re.compile(rf"--tls-everywhere ({OPTIONS.pattern})")
services_pattern_str = r"(tripleo_.*)\.service\s+loaded\s+active\s+running\s"
SERVICES_PATTERN = re.compile(services_pattern_str)


def satisfy_regex_match(model: Dict[str, str], pattern: Pattern,
                        field_to_check: str) -> bool:
    """Check whether model (job or build) should be included according to
    the user input.
    The model should be added if the information provided field_to_check
    (the model name or url for example) is matches the regex pattern.

    :param model: model information obtained from jenkins
    :param pattern: regex patter that the model name should match
    :param field_to_check: model field to perform the check
    :returns: Whether the model satisfies user input
    """
    return re.search(pattern, model[field_to_check]) is not None


def satisfy_exact_match(model: Dict[str, str], user_input: Argument,
                        field_to_check: str) -> bool:
    """Check whether model should be included according to the user input. The
    model should be added if the information provided field_to_check
    (the model name or url for example) is present in the user_input values.

    :param model: model information obtained from jenkins
    :param user_input: input argument specified by the user
    :param field_to_check: Job field to perform the check
    :returns: Whether the model satisfies user input
    """
    return model[field_to_check] in user_input.value


def satisfy_case_insensitive_match(model: Dict[str, str], user_input: Argument,
                                   field_to_check: str,
                                   default_user_value: Optional[List[str]]
                                   = None
                                   ) -> bool:
    """Check whether model should be included according to the user input. The
    model should be added if the information provided field_to_check
    (the model name or url for example) is an exact case-insensitive match to
    the information in the user_input values.

    :param model: model information obtained from jenkins
    :param user_input: input argument specified by the user
    :param field_to_check: Job field to perform the check
    :param default_user_value: Default value to use if the user input contains
    no value
    :returns: Whether the model satisfies user input
    """
    if model[field_to_check] is None:
        return False
    value = user_input.value
    if not value and default_user_value:
        value = default_user_value
    lowercase_input = [status.lower() for status in value]
    return model[field_to_check].lower() in lowercase_input


def satisfy_range_match(model: Dict[str, str], user_input: Argument,
                        field_to_check: str) -> bool:
    """Check whether model should be included according to the user input. The
    model should be added if the information provided in field_to_check
    (the model name or url for example) is consistent with the range defined
    in the user_input values.

    :param model: model information obtained from jenkins
    :param user_input: input argument specified by the user
    :param field_to_check: Job field to perform the check
    :returns: Whether the model satisfies user input
    """
    model_value = float(model[field_to_check])
    results = [RANGE_OPERATORS[operator](float(model_value), float(user_value))
               for operator, user_value in user_input.value]
    return all(results)


def filter_topology(model: Dict[str, str], operator: str, value: str,
                    component: str) -> bool:
    """Check whether model should be included according to the user input. The
    model should be added if the its topology is consistent with the components
    requested by the user (number of controller or compute nodes).

    :param model: model information obtained from jenkins
    :param operator: operator to filter the topology with
    :param value: Value to use in the comparison
    :param component: Component of the topology to filter
    :returns: Whether the model satisfies user input
    """
    topology = model["topology"]
    for part in topology.split(","):
        if component in part:
            _, amount = part.split(":")
            return RANGE_OPERATORS[operator](float(amount), float(value))
    return False


def matches_regex(pattern: str, string: str, flags: int = 0) -> bool:
    """Checks if a certain text is matched by a regex pattern.

    Examples
    --------
    >>> matches_regex('success', 'SUCCESS', flags=re.I)
    True

    :param pattern: The pattern to test.
    :param string: The text to test the pattern against.
    :param flags: Modifiers for the matching operation.
    :return: True if the string matched the pattern, false if not.
    """
    try:
        return bool(re.search(pattern, string, flags))
    except sre_constants.error:
        return False  # Do not crash against invalid patterns


def apply_filters(iterable: Iterable, *filters: Callable) -> Iterable:
    """Returns a collection containing the items from the iterable that
    satisfy all the conditions passed as filters.

    Filters are AND'd together, meaning that an item has to pass all of them in
    order to appear on the result.

    Examples
    -------
    >>> apply_filters([1, 2, 3], lambda x: x > 1, lambda x: x < 3)
    [2]

    :param iterable: The collection to filter.
    :param filters: List of filters to apply.
    :return: The collection post-filtering.
    """
    result = list(iterable)

    for check in filters:
        result = list(filter(check, result))

    return result
