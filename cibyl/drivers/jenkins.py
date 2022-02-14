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
import sys

import urllib3
from requests import Session, adapters

from cibyl.models.ci.job import Job

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.getLogger("requests").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)

LOG = logging.getLogger(__name__)


class Jenkins(object):

    def __init__(self, url, **kwargs):
        self.url = url

    def make_api_call(self):
        session = Session()
        max_retries = -1
        adapter = adapters.HTTPAdapter(max_retries=max_retries)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        resp = session.request('GET', self.url + "/api/json", verify=False)
        return resp.json()

    def query(self, environment, args):
        LOG.debug("querying Jenkins: {}".format(self.url))
        if 'jobs' in args or 'jobs_regex' in args:
            result_json = self.make_api_call()
            for job_dict in result_json['jobs']:
                for system in environment.systems:
                    if system.type.data == 'jenkins':
                        if not args.get('jobs') and not args.get('jobs_regex'):
                            system.jobs.append(Job(name=job_dict['name']))
                        else:
                            if args.get('jobs') and args.get('jobs_regex'):
                                LOG.error("Oh no you didn't!")
                                sys.exit(2)
                            elif args.get('jobs'):
                                for job in args['jobs']:
                                    if job.name.data in job_dict.get('name'):
                                        if system.jobs_scope.data:
                                            for scope in system.jobs_scope.data:  # noqa
                                                if re.search(scope,
                                                             job_dict['name']):
                                                    system.jobs.append(Job(
                                                        name=job_dict['name']))
                                        else:
                                            system.jobs.append(Job(
                                                name=job_dict['name']))
                                        break
                            elif args.get('jobs_regex'):
                                for regex in args.get('jobs_regex'):
                                    if re.search(regex.name.data,
                                                 job_dict['name']):
                                        if system.jobs_scope.data:
                                            for scope in system.jobs_scope.data:  # noqa
                                                if re.search(scope,
                                                             job_dict['name']):
                                                    system.jobs.append(Job(name=job_dict['name']))  # noqa
                                        else:
                                            system.jobs.append(Job(
                                                name=job_dict['name']))
                                        break
        return environment
