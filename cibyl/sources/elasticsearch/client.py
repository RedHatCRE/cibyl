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

from elasticsearch import Elasticsearch

from cibyl.exceptions.elasticsearch import ElasticSearchError

LOG = logging.getLogger(__name__)


class ElasticSearchClient:
    """Elasticsearch client to connect to the instance
    and retrieve the data from this one"""

    def __init__(self,
                 host: str = "http://localhost",
                 port: int = 9200) -> None:
        """Initialization of ElasticSearchClient

        :param host: Elasticsearch host including the scheme
        :type host: str, optional
        :param port: Port for sending REST requests to the instance
        :type port: str, optional"""
        self.address = f"{host}:{port}"
        self.connection = None

    def connect(self) -> 'ElasticSearchClient':
        """Connects to the elasticsearch instance

        :return: Elasticsearch module instance
        :raises: ElasticSearchError:
                 If exists an unhandled connection error
        """
        if self.connection:
            self.disconnect()
        self.connection = Elasticsearch(self.address)
        if not self.connection.ping():
            message = 'Error connecting to '
            message += f"Elasticsearch: {self.address}"
            raise ElasticSearchError(message)
        LOG.debug(f"Connection established successfully with elasticsearch"
                  f" instance: {self.address}")
        return self

    def disconnect(self) -> None:
        """Explicitly closes connections with the
        elasticsearch instance

        :return: None
        """
        try:
            self.connection.transport.close()
            LOG.debug(f"Connection successfully closed with elasticsearch"
                      f" instance: {self.address}")
        except Exception:
            message = 'Could not close the connextion with elasticsearch'
            message += f" instance: {self.address}"
            LOG.error(message)
