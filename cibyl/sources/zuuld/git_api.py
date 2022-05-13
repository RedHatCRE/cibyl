import base64
import json
import logging
import os
import urllib

import requests
import yaml

from cibyl.exceptions.zuul import RateLimitException
from cibyl.models.attribute import AttributeDictValue
from cibyl.models.ci.base.job import Job
from cibyl.models.ci.zuul.tenant import Tenant
from cibyl.sources.git import GitSource
from cibyl.utils.yaml import get_loader

ZUUL_JOBS_LOCATION = ['zuul.d', '.zuul.yaml']
LOG = logging.getLogger(__name__)


class ZuulGitHub:
    """
    ZuulGitHub class will provide functionality to read
    Zuul jobs from github repository.
    """
    def __init__(self, kwargs=None):
        if kwargs is None:
            kwargs = {}
        self.git_base_url = "https://api.github.com/repos/{}/git/trees/master"
        self.job_dir = "zuul.d"
        self.username = kwargs.get("username", "")
        self.token = kwargs.get("token", "")
        self.repos = kwargs.get('repos', None)
        self._validate()

    def _validate(self):
        # validate url
        for repo in self.repos:
            try:
                result = urllib.parse.urlparse(repo.get('url'))
                self.scheme = result.scheme
                self.netloc = result.netloc
                if result.path.endswith(".git"):
                    temp_path = result.path.split(".git")[0]
                    if temp_path.startswith("/"):
                        temp_path = temp_path.lstrip("/")
                else:
                    if result.path.startswith("/"):
                        temp_path = result.path.lstrip("/")

                self.path = repo['repo_name'] = temp_path
                self.params = result.params
                self.query = result.query
            except Exception as e:
                raise urllib.error.URLError("Invalid url") from e

    def _make_request(self, url=None):
        """
        Make github requests
        """
        if not url:
            url = self.req_url
        authorization = f'token {self.token}'
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": authorization,
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return json.loads(response.text)
        elif response.status_code == 403:
            raise RateLimitException

    def _get_job_dir_url(self, repo):
        """
        List github directory
        """
        text = self._make_request(self.git_base_url.format(
            repo.get('repo_name')))
        for i in text['tree']:
            if i['path'] in ZUUL_JOBS_LOCATION:
                return i
        return None

    def get_file_list(self, repo):
        """
        Get files in directory
        """
        files_json = self._get_job_dir_url(repo)
        if files_json:
            zuul_d_files = self._make_request(files_json['url'])
            files_list = []
            if zuul_d_files:
                for f in zuul_d_files['tree']:
                    if f['path'].endswith(".yaml") or \
                            f['path'].endswith(".yml"):
                        files_list.append((f['path'], f['url']))
            return files_list

    def _decode_files(self, repo):
        """
        Decode files which are base64 encoded
        """
        files_dict = {}
        file_names = self.get_file_list(repo)
        for (name, url) in file_names:
            response = self._make_request(url)
            content = response['content']
            decoded_bytes = base64.b64decode(content)
            decoded_str = str(decoded_bytes, "utf-8")
            files_dict[name] = decoded_str
        return files_dict

    def get_jobs(self):
        """
        This method will get jobs and print
        :return:
        """
        t = Tenant(name="openstack")
        for repo in self.repos:
            files_dict = self._decode_files(repo)
            for key, value in files_dict.items():
                LOG.debug("Reading: %s", key)
                try:
                    jobs_data = yaml.load(value, Loader=get_loader())
                except Exception as e:
                    LOG.error(e)
                    LOG.error("Failed to load: %s", key)
                for i in jobs_data:
                    # This will skip project-templates etc only
                    # mapping for job
                    if 'job' in i.keys():
                        name = i['job']['name']
                        t.add_job(Job(name=name))
        return AttributeDictValue("tenant", attr_type=Tenant,
                                  value={"openstack": t})


class ZuulLocal(GitSource):
    """
    ZuulLocal class will provide functionality to read
    Zuul jobs from files.
    """
    def __init__(self, kwargs=None):
        if kwargs is None:
            kwargs = {}
        self.repos = kwargs.get("repos")
        super(ZuulLocal, self).__init__(repos=self.repos)

    def _validate(self):
        # Check repo exists, if yes pull latest changes
        self.setup()

        # First check for directory then for file
        for repo in self.repos:
            if os.path.isdir(os.path.join(repo.get('dest'),
                                          ZUUL_JOBS_LOCATION[0])):
                repo['jobs_dir'] = "zuul.d"
            elif os.path.isfile(os.path.join(repo.get('dest'),
                                             ZUUL_JOBS_LOCATION[1])):
                repo['jobs_file'] = ".zuul.yaml"

    def get_file_list(self):
        """
        This method will give list of files in zuul jobs dir.
        """
        def get_yaml(x):
            return [f for f in x
                    if f.endswith('.yaml') or
                    f.endswith(".yml")]
        job_files = []
        for repo in self.repos:
            file_path = repo.get('jobs_file', None)
            jobs_dir = repo.get('jobs_dir', None)
            if file_path:
                file_path = os.path.join(repo.get('dest'), file_path)
            if jobs_dir:
                jobs_dir = os.path.join(repo.get('dest'), jobs_dir)

            if file_path and os.path.isfile(file_path):
                job_files.append(file_path)

            elif jobs_dir and os.path.isdir(jobs_dir):
                files = os.listdir(jobs_dir)
                job_files.extend([os.path.join(jobs_dir, i)
                                  for i in get_yaml(files)])
        return job_files

    def _parse_file(self, file_path):
        """
        This method will parse single file
        """
        LOG.debug("Reading: %s", file_path)
        if os.path.isfile(file_path):
            try:
                with open(file_path, "rb") as f:
                    return yaml.load(f.read(), Loader=get_loader())
            except Exception as e:
                LOG.error(e)
                LOG.error("Not able to read: %s", file_path)
                # Printing only error message. We need to traverse all files
                # Error message will tell which file not able to parse.
        else:
            raise FileNotFoundError("File not exist: %s", file_path)

    def get_jobs(self):
        """
        This method will parse jobs from file
        """
        t = Tenant(name='openstack')
        for f in self.get_file_list():
            LOG.debug("Parsing: %s", f)
            json_data = self._parse_file(f)
            for job in json_data:
                if 'job' in job.keys():
                    name = job['job']['name']
                    t.add_job(Job(name=name))

        return AttributeDictValue("tenant", attr_type=Tenant,
                                  value={'openstack': t})
