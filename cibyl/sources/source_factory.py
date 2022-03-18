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
from cibyl.sources.jenkins_job_builder import JenkinsJobBuilder
from cibyl.sources.zuul.source import Zuul


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
        :param kwargs: Collection of data that further describes the source.
        :type kwargs: str
        :return: A new instance.
        :rtype: :class:`cibyl.sources.source.Source`
        """
        if source_type == SourceType.JENKINS:
            return Jenkins(name=name, **kwargs)

        if source_type == SourceType.ZUUL:
            return SourceFactory.build_zuul_source(name=name, **kwargs)

        if source_type == SourceType.ELASTICSEARCH:
            raise NotImplementedError(
                f"Source '{source_type}' not yet implemented."
            )

        if source_type == SourceType.JENKINS_JOB_BUILDER:
            return JenkinsJobBuilder(name=name, **kwargs)

        raise NotImplementedError(f"Unknown source type '{source_type}'")

    @staticmethod
    def build_zuul_source(**kwargs):
        """Builds a new Zuul source.

        :param kwargs: Collection of data that further describes the source.
        :type kwargs: str
        :return: A new instance.
        :rtype: :class:`Zuul`
        """

        def get_url():
            if 'url' not in kwargs:
                raise ValueError("Missing 'url' parameter on Zuul source.")

            # Zuul's constructor will not expect a 'url' field
            return kwargs.pop('url')

        def get_cert():
            cert = None

            if 'cert' in kwargs:
                cert = kwargs.get('cert')

            return cert

        return Zuul.new_source(get_url(), get_cert(), **kwargs)
