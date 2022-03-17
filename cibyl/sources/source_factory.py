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
from cibyl.sources.zuul.source import Zuul, ZuulData


class SourceFactory:
    @staticmethod
    def create_source(source_type, name, **kwargs):
        """
        :param source_type:
        :type source_type: str
        :param name:
        :param kwargs:
        :return:
        """
        source_type = source_type.upper()

        if source_type == 'JENKINS':
            pass
        elif source_type == 'ZUUL':
            kwargs['name'] = name

            return SourceFactory.build_zuul_source(**kwargs)
        elif source_type == 'ELASTICSEARCH':
            pass
        else:
            raise NotImplementedError(f"Unknown source type '{source_type}'")

    @staticmethod
    def build_zuul_source(**kwargs):
        def get_cert():
            cert = None

            if 'cert' in kwargs:
                cert = kwargs.get('cert')

            return cert

        def get_url():
            if 'url' not in kwargs:
                raise ValueError(
                    f"Missing 'url' parameter on Zuul source."
                )

            return kwargs.pop('url')

        return Zuul.new_source(
            get_url(),
            get_cert(),
            ZuulData(**kwargs)
        )
