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
    """Creates a new dictionary from items from another one. A new
    dictionary is formed by extracting the keys explicitly indicated. If one of
    the given keys is not present on the dictionary, it is ignored. The
    original dictionary is left untouched.

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


def nsubset(dictionary, keys):
    """Creates a new dictionary from items from another one. The 'n' stands
    for 'negative', meaning that the keys form an excluded list. All keys
    from the other dictionary will be extracted except for the ones explicitly
    indicated. The original dictionary is left untouched.

    :param dictionary: The dictionary to extract items from.
    :type dictionary: dict
    :param keys: The keys to not get from the dictionary.
    :type keys: list
    :return: The new dictionary.
    :rtype: dict
    """
    result = {}

    for key in dictionary.keys():
        # Ignore keys on the excluded list
        if key in keys:
            continue

        result[key] = dictionary[key]

    return result


def chunk_dictionary_into_lists(dictionary: dict, size: int = 300) -> list:
    """It returns a list of sub lists. Each one with the size indicated
    in the 'size' parameter where every element is the key of the dictionary
    provided. If the size is less than the quantity provided, it creates
    just one sublist with those keys.
    """
    chunked_list = []
    for chunk_max_value in range(
            0,
            len(list(dictionary.keys())),
            size
    ):
        chunked_list.append(
            list(
                dictionary.keys()
            )[chunk_max_value:chunk_max_value + size]
        )
    return chunked_list
