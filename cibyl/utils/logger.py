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
import sys

import colorlog

FORMAT_STR = '{}%(levelname)-8s %(name)-20s %(message)s'
FILE_LOGGER_FORMATER = logging.Formatter(fmt=FORMAT_STR.format(""))
TERMINAL_LOGGER_FORMATTER = colorlog.ColoredFormatter(
                                FORMAT_STR.format("%(log_color)s"),
                                log_colors=dict(
                                    DEBUG='blue',
                                    INFO='green',
                                    WARNING='yellow',
                                    ERROR='red',
                                    CRITICAL='bold_red,bg_white',))


def configure_terminal_logging(level):
    """Configure logger to print to terminal.

    :param level: Logging level, default DEBUG
    :type level: int
    """
    logger = logging.getLogger()
    logger.setLevel(level)
    stream_handler = logging.StreamHandler(sys.stderr)
    stream_handler.setLevel(level)
    stream_handler.setFormatter(TERMINAL_LOGGER_FORMATTER)
    logger.addHandler(stream_handler)


def configure_file_logging(log_file, level):
    """Configure logger to print to file.

    :param log_file: Path to log file
    :param log_file: str
    :param level: Logging level, default DEBUG
    :type level: int
    """
    logger = logging.getLogger()
    logger.setLevel(level)
    file_handler = logging.FileHandler(log_file, mode="w")
    file_handler.setLevel(level)
    file_handler.setFormatter(FILE_LOGGER_FORMATER)
    logger.addHandler(file_handler)


def configure_logging(log_config, level=logging.INFO):
    """Configure logging format and level.

    :param log_config: Configuration for the logger
    :type log_config: dict
    :param level: Logging level, default DEBUG
    :type level: int
    """
    if log_config.get("debug", False):
        level = logging.DEBUG
    log_mode = log_config["log_mode"]
    log_file = log_config["log_file"]
    if log_mode == "terminal":
        print(log_mode, log_file)
        configure_terminal_logging(level)
    elif log_mode == "file":
        configure_file_logging(log_file, level)
    else:
        configure_terminal_logging(level)
        configure_file_logging(log_file, level)
