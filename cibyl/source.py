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
import importlib


class Source:
    """
    """
    def __init__(self, name: str, driver: str, priority: int = -1,
                 **kwargs):
        """
        Initialize source class.
        :param name:
        :param driver:
        :param priority:
        :param kwargs:
        """
        self.name = name
        self.driver = driver
        self.priority = priority
        self.driver = driver
        self.driver_dict = kwargs

    def get_driver_module(self, module_name):
        """
        Get driver module
        :param module_name:
        :return:
        """
        return getattr(importlib.import_module(
            "cibyl.drivers.{}".format(self.driver)), module_name)

    def populate(self, environment, args):
        """
        Populate source
        :param environment:
        :param args:
        :return:
        """
        try:
            driver = self.get_driver_module(self.driver.capitalize())
        except AttributeError:
            driver = self.get_driver_module(self.driver.upper())
        driver_instance = driver(**self.driver_dict)
        driver_instance.query(environment, args)
