# Copyright 2022 Red Hat
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
from cibyl.models.ci.job import Job

import logging
from requests import adapters
from requests import Session
import urllib3

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
        if 'jobs' in args:
            result_json = self.make_api_call()
            for job_dict in result_json['jobs']:
                for system in environment.systems:
                    if system.type.data == 'jenkins':
                        if not args['jobs']:
                            system.jobs.append(Job(name=job_dict['name']))
                        else:
                            for job_pattern in args['jobs']:
                                if job_pattern.name.data in job_dict['name']:
                                    system.jobs.append(Job(
                                        name=job_dict['name']))
                                    break
        return environment
