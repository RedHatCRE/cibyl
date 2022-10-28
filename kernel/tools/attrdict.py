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


class AttrDict(dict):
    """A dictionary that allows you to access its items as attributes, meaning
    that the following: "dict['item']" can also be written as "dict.item".
    """
    __setattr__ = dict.__setattr__

    def __getattr__(self, attribute):
        """Define __getattr__ to reuse __getitem__ but raise AttributeError
        instead of KeyError, so we can use hasattr with child classes.
        """
        try:
            return self.__getitem__(attribute)
        except KeyError as ex:
            raise AttributeError from ex
