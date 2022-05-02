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
import logging

LOG = logging.getLogger(__name__)


def subset(dictionary, keys):
    """Creates a new dictionary from items from another one.

    :param dictionary: The dictionary to extract items from.
    :type dictionary: dict
    :param keys: The keys to get from the dictionary.
    :type keys: list
    :return: The new dictionary.
    :rtype: dict
    """
    result = {}

    for key in keys:
        # Do not crash if a key is not present
        if key not in dictionary:
            message = "Ignoring key '%s' not found in dictionary: %s"
            LOG.debug(message, key, dictionary)
            continue

        result[key] = dictionary[key]

    return result
