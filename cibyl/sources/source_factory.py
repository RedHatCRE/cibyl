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
from enum import Enum

from cibyl.sources.jenkins import Jenkins


class SourceType(str, Enum):
    JENKINS = 'jenkins',
    ZUUL = 'zuul',
    ELASTICSEARCH = 'elasticsearch'


class SourceFactory:
    @staticmethod
    def create_source(source_type, name, **kwargs):
        """
        :param source_type:
        :type source_type: str or :class:`SourceType`
        :param name:
        :param kwargs:
        :return:
        """
        source_type = source_type.lower()

        if source_type == SourceType.JENKINS:
            return Jenkins(name=name, **kwargs)
        elif source_type == SourceType.ZUUL:
            return None
        elif source_type == SourceType.ELASTICSEARCH:
            return None
        else:
            raise NotImplementedError(f"Unknown source type '{source_type}'")
