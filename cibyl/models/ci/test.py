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
from cibyl.value import Value


class Test(object):

    def __init__(self, name: str, class_name: str):

        self.class_name = Value(name='class_name',
                                arg_name='--test-class-name', type=str)
        self.name = Value(name='name', arg_name='--system-name', type=str)
