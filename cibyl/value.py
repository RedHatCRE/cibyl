# Copyright 2022 Red Hat
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
import logging

LOG = logging.getLogger(__name__)


class ValueInterface(object):

    def __init__(self, name, args=None, type=None,
                 description=None, populate=False,
                 nargs=1):
        self.name = name
        self.args = args
        self.type = type
        self.description = description
        self.populate = populate
        self.nargs = nargs


class Value(ValueInterface):

    def __init__(self, name, args=None, type=None, data=[],
                 description=None, nargs=1):
        super(Value, self).__init__(name, args, type, description,
                                    nargs=nargs)
        self.data = data


class ListValue(ValueInterface):

    def __init__(self, name, args=None, type=None, data=None,
                 description=None, nargs=1):
        super(ListValue, self).__init__(name, args=args, type=type,
                                        description=description,
                                        nargs=nargs)
        if isinstance(data, list):
            self.data = data
        if data is None:
            self.data = []

    def append(self, item):
        self.data.append(item)

    def __getitem__(self, val):
        return self.data[val]

    def __lt__(self, other):
        return self < other
