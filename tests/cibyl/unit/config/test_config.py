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
from tempfile import NamedTemporaryFile
from unittest import TestCase
from unittest.mock import Mock, patch

import yaml

import cibyl.config
from cibyl.config import Config, ConfigFactory
from cibyl.exceptions.cli import AbortedByUserError
from cibyl.exceptions.config import ConfigurationNotFound, EmptyConfiguration
from cibyl.utils.net import DownloadError
from cibyl.utils.yaml import encrypted_constructor, get_loader


class TestConfig(TestCase):
    """Test cases for the 'Config' class.
    """

    def test_empty_config(self):
        """Test that parsing and empty configuration file raises and error."""
        with NamedTemporaryFile() as config_file:
            config = Config()
            self.assertRaises(EmptyConfiguration, config.load_from_path,
                              path=config_file.name)

    def test_contents_are_loaded(self):
        """Checks that the contents of the loaded file are made available by
        the class.
        """
        yaml_return = {
            'node_a': {
                'name': 'Test',
                'host': 'test_host'
            }
        }
        with NamedTemporaryFile() as config_file:
            with patch('cibyl.config.yaml') as yaml_patched:

                yaml_patched.parse.return_value = yaml_return

                config = Config()
                config.load_from_path(path=config_file.name)
                yaml_patched.parse.assert_called_with(config_file.name)

            self.assertEqual(config, yaml_return)

    def test_encrypted_constructor(self):
        self.assertEqual('', encrypted_constructor(yaml.SafeLoader,
                                                   yaml.Node))

    def test_yaml_loader(self):
        yaml_text = """
---
- secret:
    name: ansible_galaxy_info_tripleo_ci
    data:
      url: https://galaxy.ansible.com
      token: !encrypted/pkcs1-oaep
        - asdjflasdj
        """
        data = yaml.load(yaml_text, Loader=get_loader())
        self.assertIn('secret', data[0].keys())
        self.assertIs('', data[0]['secret']['data']['token'])


class TestConfigFromSearch(TestCase):
    """Tests for :meth:`cibyl.config.ConfigFactory.from_search`.
    """

    def test_error_on_nothing_found(self):
        """Checks that :class:`ConfigurationNotFound` is thrown if there is
        no file among the default paths.
        """
        available_call = cibyl.config.get_first_available_file = Mock()

        available_call.return_value = None

        with self.assertRaises(ConfigurationNotFound):
            ConfigFactory.from_search()

    def test_config_from_file(self):
        """Checks that the configuration file is created from the found file.
        """
        file = 'some/file'

        available_call = cibyl.config.get_first_available_file = Mock()
        from_file_call = cibyl.config.ConfigFactory.from_file = Mock()

        available_call.return_value = file

        ConfigFactory.from_search()

        from_file_call.assert_called_once_with(file)


class TestConfigFromURL(TestCase):
    """Tests for :meth:`cibyl.config.ConfigFactory.from_url`.
    """

    def test_download_error(self):
        """Checks that :class:`ConfigurationNotFound` is thrown if download
        fails.
        """

        def raise_error(*_):
            raise DownloadError

        url = 'some-url'
        file = 'some/file'

        available_call = cibyl.config.is_file_available = Mock()
        download_call = cibyl.config.download_file = Mock()

        available_call.return_value = False
        download_call.side_effect = raise_error

        with self.assertRaises(ConfigurationNotFound):
            ConfigFactory.from_url(url, file)

        download_call.assert_called_with(url, file)

    def test_file_not_on_system(self):
        """Checks that the file is downloaded if it is not on the system.
        """
        url = 'some-url'
        file = 'some/file'

        available_call = cibyl.config.is_file_available = Mock()
        download_call = cibyl.config.download_file = Mock()
        from_file_call = cibyl.config.ConfigFactory.from_file = Mock()

        available_call.return_value = False
        from_file_call.return_value = Mock()

        self.assertEqual(
            from_file_call.return_value,
            ConfigFactory.from_url(url, file)
        )

        download_call.assert_called_with(url, file)
        from_file_call.assert_called_once_with(file)

    def test_deletes_file_if_it_exists(self):
        """Checks that the target file is deleted if it already exists.
        """
        url = 'some-url'
        file = 'some/file'

        overwrite_call = Mock()
        available_call = cibyl.config.is_file_available = Mock()
        delete_call = cibyl.config.os.remove = Mock()

        cibyl.config.download_file = Mock()
        cibyl.config.ConfigFactory.from_file = Mock()

        available_call.return_value = True
        overwrite_call.return_value = True

        ConfigFactory.from_url(url, file, overwrite_call)

        delete_call.assert_called_once_with(file)

    def test_aborted_by_user(self):
        """Checks that :class:`AbortedByUserError` is thrown if user says
        not to overwrite.
        """
        url = 'some-url'
        file = 'some/file'

        overwrite_call = Mock()
        available_call = cibyl.config.is_file_available = Mock()

        cibyl.config.download_file = Mock()
        cibyl.config.ConfigFactory.from_file = Mock()

        available_call.return_value = True
        overwrite_call.return_value = False

        with self.assertRaises(AbortedByUserError):
            ConfigFactory.from_url(url, file, overwrite_call)
