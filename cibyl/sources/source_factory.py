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

from cibyl.sources.elasticsearch.api import ElasticSearchOSP
from cibyl.sources.jenkins import Jenkins
from cibyl.sources.jenkins_job_builder import JenkinsJobBuilder


class SourceType(str, Enum):
    """Describes the sources known by the app, those which can be build.
    """
    JENKINS = 'jenkins'
    ZUUL = 'zuul'
    ELASTICSEARCH = 'elasticsearch'
    JENKINS_JOB_BUILDER = 'jenkins_job_builder'


class SourceFactory:
    """Instantiates sources from inputs coming from the configuration file.
    """

    @staticmethod
    def create_source(source_type, name, **kwargs):
        """Builds a new source.

        :param source_type: Type of the source to build.
        :type source_type: str or :class:`SourceType`
        :param name: A name to identify the source.
        :type name: str
        :param kwargs: Collection of data that further describe the source.
        :type kwargs: dict
        :return: A new instance.
        :rtype: :class:`cibyl.sources.source.Source`
        """
        source_type = source_type.lower()

        if source_type == SourceType.JENKINS:
            return Jenkins(name=name, **kwargs)

        if source_type == SourceType.ZUUL:
            return None

        if source_type == SourceType.ELASTICSEARCH:
            return ElasticSearchOSP(name=name, **kwargs)

        if source_type == SourceType.JENKINS_JOB_BUILDER:
            return JenkinsJobBuilder(name=name, **kwargs)

        raise NotImplementedError(f"Unknown source type '{source_type}'")
