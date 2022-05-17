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
import os
from unittest import skipIf


def min_test_level(level):
    """Skips this test unless the 'TEST_LEVEL' environmental variable is
    equal or greater than the provided level.
    """

    def wrapper(func):
        @skipIf(
            int(os.getenv('TEST_LEVEL', 0)) < level,
            "Minimum test level not met. Increase 'TEST_LEVEL' to include "
            "this."
        )
        def test(*args, **kwargs):
            func(*args, **kwargs)

        return test

    return wrapper
