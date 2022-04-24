import base64
import json
import logging
import os
import urllib

import requests
import yaml

from cibyl.exceptions.zuul import RateLimitException
from cibyl.models.attribute import AttributeDictValue
from cibyl.models.ci.job import Job
from cibyl.sources.zuul.zuul_utils import get_loader

ZUUL_JOBS_LOCATION = ['zuul.d', '.zuul.yaml']
LOG = logging.getLogger(__name__)


class ZuulGitHub:
    # TODO PATH ?
    def __init__(self, url, kwargs={}):
        self.git_base_url = "https://api.github.com/repos/{}/git/trees/master"
        self.job_dir = "zuul.d"
        self.username = kwargs.get("username", "")
        self.token = kwargs.get("token", "")
        self.url = url
        self._validate()

        self.req_url = self.git_base_url.format(self.path)

    def _validate(self):
        # validate url
        try:
            result = urllib.parse.urlparse(self.url)
            self.scheme = result.scheme
            self.netloc = result.netloc
            if result.path.endswith(".git"):
                temp_path = result.path.strip(".git")[0]
                if temp_path.startswith("/"):
                    temp_path = temp_path.lstrip("/")
            else:
                if result.path.startswith("/"):
                    temp_path = result.path.lstrip("/")

            self.path = temp_path
            self.params = result.params
            self.query = result.query
        except Exception as e:
            raise urllib.error.URLError("Invalid url") from e
        # TODO Add validations

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
        else:
            if "API rate limit exceeded for" in response.text:
                raise RateLimitException

    def _get_job_dir_url(self):
        """
        List github directory
        """
        text = self._make_request()
        for i in text['tree']:
            if i['path'] in ZUUL_JOBS_LOCATION:
                return i
        return None

    def get_file_list(self):
        """
        Get files in directory
        """
        files_json = self._get_job_dir_url()
        if files_json:
            zuul_d_files = self._make_request(files_json['url'])
            files_list = []
            if zuul_d_files:
                for f in zuul_d_files['tree']:
                    if f['path'].endswith(".yaml") or \
                            f['path'].endswith(".yml"):
                        files_list.append((f['path'], f['url']))
            return files_list

    def _decode_files(self):
        files_dict = {}
        file_names = self.get_file_list()
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
        job_names = {}
        files_dict = self._decode_files()
        for key, value in files_dict.items():
            LOG.debug("Reading: {}".format(key))
            try:
                jobs_data = yaml.load(value, Loader=get_loader())
            except Exception as e:
                print(e)
                LOG.error("Failed to load: {}".format(key))
            for i in jobs_data:
                # This will skip project-templates etc only mapping for job.
                if 'job' in i.keys():
                    name = i['job']['name']
                    job_names[name] = Job(name=name)
        return AttributeDictValue("jobs", attr_type=Job, value=job_names)


class ZuulLocal:
    # TODO fix the repo path
    # TODO fix project path
    # TODO use temp dir
    # TODO git clone repo
    def __init__(self, repo_dir, project='openstack'):
        self.repo_dir = repo_dir
        self.project = project

    def get_file_list(self):
        """
        This method will give list of files in zuul jobs dir.
        """
        path = os.path.join(self.repo_dir, self.project)
        projects = []  # PROJECTS_DIR[self.project]
        job_files = []

        def get_yaml(x):
            return [f for f in x
                    if f.endswith('.yaml') or
                    f.endswith(".yml")]

        for project in projects:
            job_dir = os.path.join(path, project, 'zuul.d')
            files = os.listdir(job_dir)
            job_files.extend([os.path.join(job_dir, i)
                              for i in get_yaml(files)])

        return job_files

    def _parse_file(self, file_path):
        """
        This method will parse single file
        """
        LOG.debug("Reading: {}".format(file_path))
        if os.path.isfile(file_path):
            try:
                data = open(file_path, "rb").read()
                return yaml.load(data, Loader=get_loader())
            except Exception as e:
                print(e)
                LOG.error("Not able to read: {}".format(file_path))
                # Printing only error message. We need to traverse all files
                # Error message will tell which file not able to parsed.
        else:
            raise FileNotFoundError("File not exist: {}".format(file_path))

    def get_jobs(self, json_data):
        """
        This method will parse jobs from file
        """
        all_jobs = {}
        for f in self.get_file_list():
            json_data = self._parse_file(f)
            for job in json_data:
                if 'job' in job.keys():
                    name = job['job']['name']
                    all_jobs[name] = Job(job=name)

        return AttributeDictValue("jobs", attr_type=Job, values=all_jobs)
