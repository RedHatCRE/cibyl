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

import time
from unittest import TestCase

from cibyl.utils.status_bar import StatusBar


class TestStatusBar(TestCase):
    """Test StatusBar class"""

    def setUp(self):
        self.status_bar = StatusBar("Sending a query")

    def tearDown(self):
        if self.status_bar.is_alive():
            self.status_bar.stop()
            self.status_bar.join()

    def test_status_bar(self):
        """Checks that status bar starts and stops without error"""
        self.status_bar.start()
        time.sleep(0.1)
        self.status_bar.stop()

        self.assertFalse(self.status_bar.is_alive())

    def test_status_bar_context_manager_success(self):
        """Checks that StatusBar works correctly as context manager"""
        with self.status_bar:
            time.sleep(0.1)

        self.assertFalse(self.status_bar.is_alive())

    def test_status_bar_context_manager_fail(self):
        """Checks that status bar ends when Exception is raised"""
        try:
            with self.status_bar:
                time.sleep(0.1)
                raise Exception
        except Exception:
            pass

        self.assertFalse(self.status_bar.is_alive())
