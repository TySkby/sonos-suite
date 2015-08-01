# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


def normalize_single_command_argument(command_argument):
    command_argument = command_argument.strip()
    if command_argument.isdigit():
        return int(command_argument)
    return command_argument


def normalize_all_command_arguments(command_arguments):
    return [normalize_single_command_argument(command_argument) for command_argument in command_arguments]
