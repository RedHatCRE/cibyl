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
from urllib.parse import urlsplit

from cibyl.cli.argument import Argument
from cibyl.exceptions.elasticsearch import ElasticSearchError
from cibyl.models.attribute import AttributeDictValue
from cibyl.models.ci.build import Build
from cibyl.models.ci.job import Job
from cibyl.sources.elasticsearch.client import ElasticSearchClient
from cibyl.sources.source import Source

LOG = logging.getLogger(__name__)


class ElasticSearchOSP(Source):
    """Used to perform queries in elasticsearch"""

    def __init__(self: object, driver: str = 'elasticsearch',
                 name: str = "elasticsearch", priority: int = 0,
                 **kwargs) -> None:
        super().__init__(name=name, driver=driver, priority=priority)

        if 'elastic_client' in kwargs:
            self.es_client = kwargs.get('elastic_client')
        else:
            try:
                url_parsed = urlsplit(kwargs.get('url'))
                host = f"{url_parsed.scheme}://{url_parsed.hostname}"
                port = url_parsed.port
            except Exception as exception:
                raise ElasticSearchError('The URL given is not valid') \
                      from exception
            self.es_client = ElasticSearchClient(host, port)

    def get_jobs(self: object, **kwargs: Argument) -> list:
        self.es_connection = self.es_client.connect()
        """Get jobs from elasticsearch

            :returns: Job objects queried from elasticserach
            :rtype: :class:`AttributeDictValue`
        """
        jobs_provided = kwargs.get('jobs').value

        query_body = QueryTemplate('jobName', jobs_provided).get

        hits = self.__query_get_hits(
            index='jenkins',
            query=query_body
        )

        job_objects = {}
        for hit in hits:
            job_name = hit['_source']['jobName']
            url = hit['_source']['envVars']['JOB_URL']
            job_objects[job_name] = Job(name=job_name, url=url)
        return AttributeDictValue("jobs", attr_type=Job, value=job_objects)

    def __query_get_hits(self: object, query: dict, index: str = '') -> list:
        """Perform the search query to ElasticSearch
        and return all the hits

        :param query: Query to perform
        :type query: dict
        :param index: Index
        :type index: str
        :return: List of hits.
        """
        try:
            response = self.es_connection.search(
                index=index,
                body=query,
                size=1000
            )
        except Exception as exception:
            raise ElasticSearchError("Error getting the results") \
                  from exception
        return response['hits']['hits']

    def get_builds(self: object, **kwargs: Argument):
        """
            Get builds from elasticsearch server.

            :returns: container of jobs with build information from
            elasticsearch server
            :rtype: :class:`AttributeDictValue`
        """
        jobs_found = self.get_jobs(**kwargs)

        for job_name, job in jobs_found.items():
            query_body = QueryTemplate('jobName',
                                       [job_name],
                                       query_type='match').get

            builds = self.__query_get_hits(
                query=query_body
            )

            build_statuses = []
            if 'build_status' in kwargs:
                build_statuses = [status.upper()
                                  for status in
                                  kwargs.get('build_status').value]

            for build in builds:

                build_result = None
                if not build['_source']['buildResult'] and \
                        build['_source']['currentBuildResult']:
                    build_result = build['_source']['currentBuildResult']
                else:
                    build_result = build["_source"]['buildResult']

                if 'build_status' in kwargs and \
                        build['_source']['buildResult'] not in build_statuses:
                    continue

                job.add_build(Build(str(build['_source']['buildID']),
                                    build_result,
                                    build['_source']['runDuration']))

        if 'last_build' in kwargs:
            return self.get_last_build(jobs_found)

        return jobs_found

    def get_last_build(self: object, builds_jobs: AttributeDictValue):
        """
            Get last build from builds. It's determinated
            by the build_id

            :returns: container of jobs with last build information
            :rtype: :class:`AttributeDictValue`
        """
        job_object = {}
        for job_name, build_info in builds_jobs.items():
            builds = build_info.builds
            last_build_number = sorted(builds.keys(), key=int)[-1]
            last_build_info = builds[last_build_number]
            # Now we need to consturct the Job object
            # with the last build object in this one
            build_object = Build(str(last_build_info.build_id),
                                 str(last_build_info.status))
            job_object[job_name] = Job(name=job_name)
            job_object[job_name].add_build(build_object)

        return AttributeDictValue("jobs", attr_type=Job, value=job_object)


class QueryTemplate():
    """Used for template and substitutions according to the
       elements received and return a dictionary equivalent to
       a DSL query
    """

    def __init__(self: object, search_key: str,
                 search_values: list, **kwargs) -> None:
        if not isinstance(search_values, list):
            raise TypeError(f"search_values argument received: \
                            '{search_values}' is not a list")

        # Empty query for all hits or elements
        if not search_values:
            self.query_body = ''
        # Just one element that start with string
        # is better to use 'match_phrase_prefix'
        elif len(search_values) == 1:
            query_type = 'match_phrase_prefix'

            if 'query_type' in kwargs:
                query_type = kwargs.get('query_type')

            self.query_body = {
                'query': {
                    query_type: {
                        search_key: search_values[0]
                    }
                }
            }
        # If we want to find more than one element and all of them
        # start with string we need to search using OR condition
        else:
            match_to_process = {
                'should': [],
                "minimum_should_match": 1
            }

            for value in search_values:
                match_to_process['should'].append(
                    {
                        "match_phrase": {
                            search_key: value
                        }
                    }
                )

            self.query_body = {
                'query': {
                    'bool': match_to_process,
                }
            }

    @property
    def get(self: object) -> dict:
        """Return DSL query in dictionary format"""
        return self.query_body
