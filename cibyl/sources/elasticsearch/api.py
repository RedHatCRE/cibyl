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
from urllib.parse import urlsplit

from elasticsearch.helpers import scan

from cibyl.cli.argument import Argument
from cibyl.cli.ranged_argument import RANGE_OPERATORS
from cibyl.exceptions.elasticsearch import ElasticSearchError
from cibyl.models.attribute import AttributeDictValue
from cibyl.models.ci.base.build import Build
from cibyl.models.ci.base.job import Job
from cibyl.models.ci.base.test import Test
from cibyl.sources.elasticsearch.client import ElasticSearchClient
from cibyl.sources.server import ServerSource
from cibyl.sources.source import speed_index
from cibyl.utils.dicts import chunk_dictionary_into_lists

LOG = logging.getLogger(__name__)


class ElasticSearch(ServerSource):
    """Elasticsearch Source"""

    def __init__(self, driver: str = 'elasticsearch',
                 name: str = "elasticsearch", priority: int = 0,
                 elastic_client: object = None,
                 enabled: bool = True, url: str = None) -> None:
        super().__init__(name=name, driver=driver, priority=priority,
                         enabled=enabled)
        self.url = url
        self.es_client = elastic_client

    def setup(self):
        """ Ensure that a connection to the elasticsearch server can be
        established.
        """
        if self.es_client is None:
            try:
                url_parsed = urlsplit(self.url)
                host = f"{url_parsed.scheme}://{url_parsed.hostname}"
                port = url_parsed.port
            except Exception as exception:
                raise ElasticSearchError(
                    'The URL given is not valid'
                ) from exception
            self.es_client = ElasticSearchClient(host, port).connect()

    @speed_index({'base': 1})
    def get_jobs(self: object, **kwargs: Argument) -> list:
        """Get jobs from elasticsearch

            :returns: Job objects queried from elasticsearch
            :rtype: :class:`AttributeDictValue`
        """
        key_filter = 'job_name'
        jobs_to_search = []
        jobs_scope_pattern = None
        if 'jobs' in kwargs:
            jobs_to_search = kwargs.get('jobs').value
            key_filter = 'job_name'
        if 'job_url' in kwargs:
            jobs_to_search = kwargs.get('job_url').value
            key_filter = 'job_url'
        jobs_scope_arg = kwargs.get('jobs_scope')
        if jobs_scope_arg:
            jobs_scope_pattern = re.compile(jobs_scope_arg)

        # Empty query for all hits or elements
        if not jobs_to_search:
            query_body = {
                "query": {
                    "match_all": {}
                },
                "_source": ["job_name", "job_url"]
            }
        else:
            query_body = {
                'query': {
                    'match_phrase_prefix': {
                        key_filter: jobs_to_search[0]
                    }
                },
                "_source": ["job_name", "job_url"]
            }

        hits = self.__query_get_hits(
            query=query_body,
            index='logstash_jenkins_jobs'
        )

        job_objects = {}
        for hit in hits:
            job_name = hit['_source']['job_name']
            url = hit['_source']['job_url']
            if jobs_scope_pattern and not jobs_scope_pattern.search(job_name):
                continue
            job_objects[job_name] = Job(name=job_name, url=url)
        return AttributeDictValue("jobs", attr_type=Job, value=job_objects)

    def __query_get_hits(self: object,
                         query: dict,
                         index: str = '*') -> list:
        """Perform the search query to ElasticSearch
        and return all the hits

        :param query: Query to perform
        :type query: dict
        :param index: Index
        :type index: str
        :return: List of hits.
        """
        try:
            LOG.debug("Using the following query: {}"
                      .format(str(query).replace("'", '"')))
            # https://github.com/elastic/elasticsearch-py/issues/91
            # For aggregations we should use the search method of the client
            if 'aggs' in query:
                results = self.es_client.search(
                    index=index,
                    body=query,
                    size=10000,
                )
                aggregation_key = list(results['aggregations'].keys())[0]
                buckets = results['aggregations'][aggregation_key]['buckets']
                return buckets
            # For normal queries we can use the scan helper
            hits = [item for item in scan(
                self.es_client,
                index=index,
                query=query,
                size=10000
            )]
            return hits
        except Exception as exception:
            raise ElasticSearchError(
                "Error getting the results."
            ) from exception

    @speed_index({'base': 2})
    def get_builds(self: object, **kwargs: Argument):
        """
            Get builds from elasticsearch server.

            :returns: container of jobs with build information from
            elasticsearch server
            :rtype: :class:`AttributeDictValue`
        """
        jobs_found = self.get_jobs(**kwargs)

        query_body = {
            "query": {
              "bool": {
                "should": []
              }
            }
        }

        def append_job_match_to_query(job_name: str):
            query_body['query']['bool']['should'].append(
                {
                  "match": {
                    "job_name": f"{job_name}"
                  }
                }
            )

        for _, job in jobs_found.items():

            chunked_list_of_jobs = chunk_dictionary_into_lists(
                jobs_found,
                400
            )

        builds = []
        for jobs_list in chunked_list_of_jobs:
            for job in jobs_list:
                append_job_match_to_query(job)

            builds_results = self.__query_get_hits(
                query=query_body,
                index='jenkins_builds'
            )
            if builds_results:
                for build in builds_results:
                    builds.append(build)

            query_body['query']['bool']['should'].clear()

        build_statuses = []
        if 'build_status' in kwargs:
            build_statuses = [status.upper()
                              for status in
                              kwargs.get('build_status').value]

        build_id_argument = None
        if 'builds' in kwargs:
            build_id_argument = kwargs.get('builds').value

        for build in builds:
            build_result = None
            if not build['_source']['build_result'] and \
                    build['_source']['current_build_result']:
                build_result = build['_source']['current_build_result']
            else:
                build_result = build["_source"]['build_result']

            if 'build_status' in kwargs and \
                    build['_source']['build_result'] not in build_statuses:
                continue

            build_id = str(build['_source']['build_id'])
            if build_id_argument and \
                    build_id not in build_id_argument:
                continue
            job_name = build['_source']['job_name']
            jobs_found[job_name].add_build(Build(build_id,
                                           build_result,
                                           build['_source']['time_duration']))

        if 'last_build' in kwargs:
            return self.get_last_build(jobs_found)

        return jobs_found

    def get_last_build(self: object, builds_jobs: AttributeDictValue):
        """
            Get last build from builds. It's determined
            by the build_id

            :returns: container of jobs with last build information
            :rtype: :class:`AttributeDictValue`
        """
        job_object = {}
        for job_name, build_info in builds_jobs.items():
            builds = build_info.builds

            if not builds:
                continue

            last_build_number = sorted(builds.keys(), key=int)[-1]
            last_build_info = builds[last_build_number]
            # Now we need to construct the Job object
            # with the last build object in this one
            build_object = Build(str(last_build_info.build_id),
                                 str(last_build_info.status))
            job_object[job_name] = Job(name=job_name)
            job_object[job_name].add_build(build_object)

        return AttributeDictValue("jobs", attr_type=Job, value=job_object)

    @speed_index({'base': 3})
    def get_tests(self, **kwargs):
        """
            Get tests for a elasticsearch job.

            :returns: container of jobs with the last completed build
            (if any) and the tests
            :rtype: :class:`AttributeDictValue`
        """
        self.check_builds_for_test(**kwargs)

        job_builds_found = self.get_builds(**kwargs)
        query_body = {
            "query": {
                "bool": {
                    "must": [
                        {},
                        {
                            "bool": {
                              "should": [
                                {}
                              ]
                            }
                        },
                        {
                            "exists": {
                                "field": "test_status"
                            }
                        },
                        {
                            "exists": {
                                "field": "test_name"
                            }
                        }
                    ]
                }
            },
            "sort": [{"timestamp.keyword": {"order": "desc"}}]
        }

        test_result_argument = []
        if 'test_result' in kwargs:
            test_result_argument = [status.upper()
                                    for status in
                                    kwargs.get('test_result').value]

        test_duration_arguments = []
        if 'test_duration' in kwargs:
            test_duration_arguments = kwargs.get('test_duration').value

        hits = []
        for job in job_builds_found:
            query_body['query']['bool']['must'][0] = {
                "match": {
                    "job_name.keyword": f"{job}"
                }
            }
            builds = job_builds_found[job].builds
            for build_number in builds:
                query_body['query']['bool']['must'][1]['bool']['should'] = {
                    "match": {
                        "build_num": build_number
                    }
                }
                results = self.__query_get_hits(
                    query=query_body,
                    index='logstash_jenkins'
                )

                # We need to process all the results because
                # in the same build we can have different tests
                # So we can't use '"size": 1' in the query
                if results:
                    for result in results:
                        hits.append(result)

        for hit in hits:
            job_name = hit['_source']['job_name']
            build_number = str(hit['_source']['build_num'])
            test_name = hit['_source']['test_name']
            test_status = hit['_source']['test_status'].upper()
            class_name = hit['_source'].get(
                'test_class_name',
                None
            )
            # Check if necessary filter by Test Status:
            if test_result_argument and \
                    test_status not in test_result_argument:
                continue
            # Some build is not parsed good and contains
            # More info than a time in the field
            try:
                test_duration = hit['_source'].get(
                    'test_time',
                    None
                )
                if test_duration:
                    test_duration = float(test_duration)
            except ValueError:
                LOG.debug("'test_time' field is not well parsed in "
                          "elasticsearch for job: %s and build ID: %s",
                          job_name,
                          build_number
                          )
                continue

            if test_duration_arguments and \
               not self.match_filter_test_by_duration(
                   test_duration,
                   test_duration_arguments):
                continue

            # Duration comes in seconds. Convert to ms:
            if test_duration:
                test_duration *= 1000

            job_builds_found[job_name].builds[build_number].add_test(
                Test(
                    name=test_name,
                    result=test_status,
                    duration=test_duration,
                    class_name=class_name
                )
            )

        return job_builds_found

    def match_filter_test_by_duration(self: object,
                                      test_duration: float,
                                      test_duration_arguments: list) -> bool:
        """Match if the duration of a test pass all the
        conditions provided by the user that are located
        in the arguments

        :params test_duration: Duration of a job
        :type node_name: float
        :params test_duration_arguments: Conditions provided
        by the user
        :type list: str

        :returns: Return if match all the conditions or no
        :rtype: bool
        """
        for test_duration_argument in test_duration_arguments:
            operator = RANGE_OPERATORS[test_duration_argument.operator]
            operand = test_duration_argument.operand
            if not operator(test_duration, float(operand)):
                return False
        return True
