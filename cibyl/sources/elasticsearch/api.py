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
from cibyl.plugins.openstack.deployment import Deployment
from cibyl.sources.elasticsearch.client import ElasticSearchClient
from cibyl.sources.server import ServerSource
from cibyl.sources.source import speed_index
from cibyl.utils.filtering import IP_PATTERN

LOG = logging.getLogger(__name__)


class ElasticSearchOSP(ServerSource):
    """Used to perform queries in elasticsearch"""

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

        query_body = QueryTemplate(key_filter, jobs_to_search).get

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

    def __query_get_hits(self: object, query: dict, index: str = '*') -> list:
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
            hits = [item for item in scan(
                self.es_client,
                index=index,
                query=query,
                size=10000
            )]
        except Exception as exception:
            raise ElasticSearchError(
                "Error getting the results."
            ) from exception
        return hits

    @speed_index({'base': 2})
    def get_builds(self: object, **kwargs: Argument):
        """
            Get builds from elasticsearch server.

            :returns: container of jobs with build information from
            elasticsearch server
            :rtype: :class:`AttributeDictValue`
        """
        jobs_found = self.get_jobs(**kwargs)

        for job_name, job in jobs_found.items():
            query_body = QueryTemplate('job_name',
                                       [job_name],
                                       query_type='match').get

            builds = self.__query_get_hits(
                query=query_body,
                index='jenkins_builds'
            )

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

                job.add_build(Build(build_id,
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

    @speed_index({'base': 2})
    def get_deployment(self, **kwargs):
        """Get deployment information for jobs from elasticsearch server.

        :returns: container of jobs with deployment information from
        elasticsearch server
        :rtype: :class:`AttributeDictValue`
        """
        jobs_found = self.get_jobs(**kwargs)

        query_body = {
            "query": {
              "bool": {
                "must": [
                  {
                    "bool": {
                      "must": []
                    }
                  },
                  {
                    "bool": {
                      "should": [
                        {
                          "exists": {
                            "field": "ip_version"
                          }
                        },
                        {
                          "exists": {
                            "field": "storage_backend"
                          }
                        },
                        {
                          "exists": {
                            "field": "network_backend"
                          }
                        },
                        {
                          "exists": {
                            "field": "dvr"
                          }
                        },
                        {
                          "exists": {
                            "field": "topology"
                          }
                        }
                      ],
                      "minimum_should_match": 1
                    }
                  }
                ]
              }
            },
            "size": 1,
            "sort": [
                {
                    "timestamp.keyword": {
                        "order": "desc"
                    }
                }
            ]
        }

        results = []
        hits = []
        for job in jobs_found:
            query_body['query']['bool']['must'][0]['bool']['must'] = {
                "match": {
                    "job_name.keyword": f"{job}"
                }
            }
            results = self.__query_get_hits(
                query=query_body,
                index='logstash_jenkins'
            )
            if results:
                hits.append(results[0])

        if not results:
            return jobs_found

        ip_version_argument = None
        if 'ip_version' in kwargs:
            ip_version_argument = kwargs.get('ip_version').value
        dvr_argument = None
        if 'dvr' in kwargs:
            dvr_argument = kwargs.get('dvr').value
        release_argument = None
        if 'release' in kwargs:
            release_argument = kwargs.get('release').value
        network_argument = None
        if 'network_backend' in kwargs:
            network_argument = kwargs.get('network_backend').value
        storage_argument = None
        if 'storage_backend' in kwargs:
            storage_argument = kwargs.get('storage_backend').value
        if 'osp_release' in kwargs:
            storage_argument = kwargs.get('osp_release').value

        job_objects = {}
        for hit in hits:
            job_name = hit['_source']['job_name']
            job_url = re.compile(r"(.*)/\d").search(
                hit['_source']['build_url']
            ).group(1)

            # If the key exists assign the value otherwise assign unknown
            topology = hit['_source'].get(
                "topology", "unknown")
            network_backend = hit['_source'].get(
                "network_backend", "unknown")
            ip_version = hit['_source'].get(
                "ip_version", "unknown")
            storage_backend = hit['_source'].get(
                "storage_backend", "unknown")
            dvr = hit['_source'].get(
                "dvr", "unknown")
            osp_release = hit['_source'].get(
                "osp_release", "unknown")

            if ip_version != 'unknown':
                matches = IP_PATTERN.search(ip_version)
                ip_version = matches.group(1)

            # Check if necessary filter by IP version:
            if ip_version_argument and \
                    ip_version not in ip_version_argument:
                continue

            # Check if necessary filter by dvr:
            if isinstance(dvr_argument, list) and \
                    dvr not in dvr_argument:
                continue

            # Check if necessary filter by release version:
            if release_argument and \
                    osp_release not in release_argument:
                continue

            # Check if necessary filter by network backend:
            if network_argument and \
                    network_backend not in network_argument:
                continue

            # Check if necessary filter by storage backend:
            if storage_argument and \
                    storage_backend not in storage_argument:
                continue

            job_objects[job_name] = Job(name=job_name, url=job_url)
            deployment = Deployment(
                release=osp_release,
                infra_type='',
                nodes={},
                services={},
                ip_version=ip_version,
                topology=topology,
                network_backend=network_backend,
                dvr=dvr,
                storage_backend=storage_backend,
                tls_everywhere=''
            )

            job_objects[job_name].add_deployment(deployment)

        return AttributeDictValue("jobs", attr_type=Job, value=job_objects)

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
            self.query_body = {
                "query": {
                    "exists": {
                        "field": search_key
                    }
                }
            }
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
