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
    """Represents an error during the download of a file.
    """


def download_file(url, dest):
    """Downloads a file from a remote host into the local filesystem.

    Supported protocols are:
        * HTTP
        * HTTPS

    Examples
    --------
    >>> download_file(
            'http://localhost/file.txt', '/home/user/my-file.txt'
        )
    >>> download_file(
            'https://user@pass:localhost/file.txt, '/home/user/my-file.txt'
        )

    :param url: The URL where the file is at.
    :type url: str
    :param dest: Path where the file is going to be downloaded at. Must
        contain name of the file.
    :type dest: str
    :raise DownloadError: If the download failed.
    """
    LOG.debug('Creating path to: %s', dest)

    os.makedirs(dest, exist_ok=True)

    with requests.get(url, stream=True) as request:
        if not request.ok:
            raise DownloadError(
                f'Download failed with: {request.status_code}\n'
                f'{request.text}'
            )

        LOG.debug('Saving to: %s', dest)

        with open(dest, 'wb', encoding='utf8') as file:
            for chunk in request.iter_content(chunk_size=8 * 1024):
                file.write(chunk)
