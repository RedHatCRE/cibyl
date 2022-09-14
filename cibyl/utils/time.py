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


def as_minutes(duration: float, unit: str = "ms") -> float:
    """Converts a duration to mins.

    :param duration: The duration to convert.
    :param unit: The unit the duration is in.
    :return: The time in minutes.
    :raises: NotImplementedError if the unit is not known (milliseconds or
    seconds)
    """
    if unit == "ms":
        return duration / 60000
    elif unit == "s":
        return duration / 60
    else:
        raise NotImplementedError
