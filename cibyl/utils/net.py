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
import os

import requests

LOG = logging.getLogger(__name__)


class DownloadError(Exception):
    pass


def download_file(url, dest):
    LOG.debug(f'Creating path to: {dest}')
    os.makedirs(dest, exist_ok=True)

    with requests.get(url, stream=True) as request:
        if not request.ok:
            raise DownloadError(
                f'Download failed with: {request.status_code}\n'
                f'{request.text}'
            )

        LOG.debug(f'Saving to: {dest}')

        with open(dest, 'wb', encoding='utf8') as file:
            for chunk in request.iter_content(chunk_size=8 * 1024):
                file.write(chunk)
