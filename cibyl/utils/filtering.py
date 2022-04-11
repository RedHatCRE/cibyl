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
from cibyl.cli.ranged_argument import RANGE_OPERATORS

IP_PATTERN = re.compile("ipv(.)")
RELEASE_PATTERN = re.compile(r"\d\d\.?\d?")
TOPOLOGY_PATTERN = re.compile(r"(\d([a-zA-Z])+_?)+")
PROPERTY_PATTERN = re.compile(r"=(.*)")
NETWORK_BACKEND_PATTERN = re.compile("geneve|gre|vlan|vxlan")
STORAGE_BACKEND_PATTERN = re.compile("ceph|lvm|netapp-iscsi|netapp-nfs|swift")


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


def filter_topology(model: Dict[str, str], operator: str, value: str,
                    component: str):
    """Check whether model should be included according to the user input. The
    model should be added if the its topology is consistent with the components
    requested by the user (number of controller or compute nodes).

    :param model: model information obtained from jenkins
    :type model: str
    :param operator: operator to filter the topology with
    :type operator: str
    :param value: Value to use in the comparison
    :param value: str
    :param component: Component of the topology to filter
    :param component: str
    :returns: Whether the model satisfies user input
    :rtype: bool
    """
    topology = model["topology"]
    for part in topology.split(","):
        if component in part:
            _, amount = part.split(":")
            return RANGE_OPERATORS[operator](float(amount), float(value))
    return False


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
