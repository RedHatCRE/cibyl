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

from cibyl.models.attribute import AttributeDictValue

LOG = logging.getLogger(__name__)


def subset(dictionary: dict, keys: list) -> dict:
    """Creates a new dictionary from items from another one. A new
    dictionary is formed by extracting the keys explicitly indicated. If one of
    the given keys is not present on the dictionary, it is ignored. The
    original dictionary is left untouched.

    :param dictionary: The dictionary to extract items from.
    :param keys: The keys to get from the dictionary.
    :return: The new dictionary.
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


def nsubset(dictionary: dict, keys: list) -> dict:
    """Creates a new dictionary from items from another one. The 'n' stands
    for 'negative', meaning that the keys form an excluded list. All keys
    from the other dictionary will be extracted except for the ones explicitly
    indicated. The original dictionary is left untouched.

    :param dictionary: The dictionary to extract items from.
    :param keys: The keys to not get from the dictionary.
    :return: The new dictionary.
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


def intersect_models(dict1: dict, dict2: dict) -> dict:
    """Combine two dictionaries that are returned from a source method call to
    keep only those models that are present in both. It assumes that the models
    present in both dictionaries are identical and takes them for the first
    input dictionary.

    :param dict1: The first dictionary with models.
    :param dict2: The second dictionary with models.
    :return: A new dictionary that contains only the models present in both
    input dictionaries.
    """
    intersection = dict1.keys() & dict2.keys()
    models = {key: dict1[key] for key in intersection}
    for key, model in models.items():
        # make sure that all the information present in models present in both
        # dictionaries is incorporated
        model.merge(dict2[key])
    return AttributeDictValue(dict1.name, attr_type=dict1.attr_type,
                              value=models)
