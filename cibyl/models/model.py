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
from cibyl.models.attribute import AttributeValue


# pylint: disable=too-few-public-methods
class Model:
    """Represents a base class inherited by CI and product models."""

    API = {}

    def __init__(self, attributes):
        for attribute_name, attribute_dict in self.API.items():
            attribute_class = attribute_dict.get('attribute_value_class',
                                                 AttributeValue)
            setattr(self, attribute_name, attribute_class(
                name=attribute_name, value=attributes[attribute_name],
                arguments=attribute_dict.get('arguments', []),
                attr_type=attribute_dict.get('attr_type')))
