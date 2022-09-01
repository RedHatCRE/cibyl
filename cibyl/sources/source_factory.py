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
import re
from enum import Enum

from cibyl.exceptions.config import (MissingSourceKey, MissingSourceType,
                                     NonSupportedSourceKey,
                                     NonSupportedSourceType)
from cibyl.sources.elasticsearch.api import ElasticSearch
from cibyl.sources.jenkins import Jenkins
from cibyl.sources.jenkins_job_builder import JenkinsJobBuilder
from cibyl.sources.server import ServerSource
from cibyl.sources.zuul.source import Zuul
from cibyl.sources.zuuld.source import ZuulD

LOG = logging.getLogger(__name__)


class SourceType(str, Enum):
    """Describes the sources known by the app, those which can be build.
    """
    JENKINS = 'jenkins'
    ZUUL = 'zuul'
    ELASTICSEARCH = 'elasticsearch'
    JENKINS_JOB_BUILDER = 'jenkins_job_builder'
    ZUUL_D = 'zuul.d'


class SourceFactory:
    """Instantiates sources from inputs coming from the configuration file.
    """

    @staticmethod
    def extend_source(source):
        source_class = ""
        if source.__name__ == 'Jenkins':
            source_class = Jenkins
        elif source.__name__ == 'ElasticSearch':
            source_class = ElasticSearch
        elif source.__name__ == 'Zuul':
            source_class = Zuul
        elif source.__name__ == 'JenkinsJobBuilder':
            source_class = JenkinsJobBuilder
        elif source.__name__ == 'ServerSource':
            source_class = ServerSource
        else:
            LOG.warning(f"Ignoring source extension for class: {source}")

        if source_class:
            for attr_name in [a for a in dir(source)
                              if not a.startswith('__')]:
                setattr(source_class, attr_name, getattr(source, attr_name))
            LOG.debug(f"Extended source '{source_class.__name__}' \
with plugin source")

    @staticmethod
    def create_source(source_type, name, **kwargs):
        """Builds a new source.

        :param source_type: Type of the source to build.
        :type source_type: str or :class:`SourceType`
        :param name: A name to identify the source.
        :type name: str
        :param kwargs: Collection of data that further describes the source.
        :type kwargs: str
        :return: A new instance.
        :rtype: :class:`cibyl.sources.source.Source`
        """
        try:
            if source_type == SourceType.JENKINS:
                return Jenkins(name=name, **kwargs)

            if source_type == SourceType.ZUUL:
                return Zuul.new_source(name=name, **kwargs)

            if source_type == SourceType.ELASTICSEARCH:
                return ElasticSearch(name=name, **kwargs)

            if source_type == SourceType.JENKINS_JOB_BUILDER:
                return JenkinsJobBuilder(name=name, **kwargs)

            if source_type == SourceType.ZUUL_D:
                return ZuulD(name=name, **kwargs)
        except TypeError as ex:
            re_unexpected_arg = re.search(r'unexpected keyword argument (.*)',
                                          ex.args[0])
            if re_unexpected_arg:
                raise NonSupportedSourceKey(
                    source_type, re_unexpected_arg.group(1))
            re_missing_arg = re.search(r'required positional argument: (.*)',
                                       ex.args[0])
            if re_missing_arg:
                raise MissingSourceKey(source_type, re_missing_arg.group(1))
            raise

        if source_type:
            raise NonSupportedSourceType(source_type, SourceType)
        else:
            raise MissingSourceType(name, SourceType)
