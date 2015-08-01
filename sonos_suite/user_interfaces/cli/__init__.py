# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import os
import pprint

from sonos_suite.user_interfaces.cli import terminal_utils
from sonos_suite.user_interfaces.utils import normalize_all_command_arguments
from sonos_suite.device_management.device_manager import SonosDeviceManager
from sonos_suite.device_management import exc


LAST_DEVICE_FILE_LOCATION = os.path.dirname(__file__) + '/.last_device'


def make_parser():
    parser = argparse.ArgumentParser(
        prog='sonos',
        description=terminal_utils.fit_text_to_terminal(
            'Execute a command on a selected Sonos player or group.'
            '\n\n'
            'Note that values provided for "--player" or "--group" arguments will be used '
            'in a best-effort attempt to match the given value against all known players or groups, '
            'respectively.'
        ),
        usage='sonos [-h] command [args [args ...]] [-p ... | -g ...]',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        'command',
        type=str,
        help='The command to run.  See "help" for available commands',
        default='help'
    )
    parser.add_argument(
        'args',
        nargs='*',
        help='Optional argument(s) to send to the command.  '
             'Multiple arguments may be provided, separated by a space.',
    )

    target_specification = parser.add_mutually_exclusive_group(required=False)
    target_specification_kwargs = dict(required=False, default=None, nargs=argparse.REMAINDER, type=str)
    target_specification.add_argument(
        '-p',
        '--player',
        help='The name (label) of the player to command.  '
             'This value is used to make a best-effort match attempt against all known players '
             '(eg. "bedroom" matches "Master Bedroom").',
        **target_specification_kwargs
    )
    target_specification.add_argument(
        '-g',
        '--group',
        help='The name (label) of the group to command.  '
             'This value is used to make a best-effort match attempt against all known groups '
             '(eg. "living" matches "Living Room, Dining Room" but not "Master Bedroom, Master Bathroom").',
        **target_specification_kwargs
    )

    return parser


def main():
    cli_manager = make_parser().parse_args()
    player_query = None
    group_query = None
    if cli_manager.player:
        player_query = ' '.join(cli_manager.player)
    elif cli_manager.group:
        group_query = ' '.join(cli_manager.group)
    elif os.path.isfile(LAST_DEVICE_FILE_LOCATION):
        with open(LAST_DEVICE_FILE_LOCATION, 'r') as fh:
            player_query = fh.readline()
        print('Searching Last Player:', player_query)
    else:
        print('Could not determine last device used!  Player will be chosen at random.')

    try:
        device_manager = SonosDeviceManager(player_query, group_query)
        with open(LAST_DEVICE_FILE_LOCATION, 'w+') as fh:
            fh.write(device_manager.device.player_name)
    except exc.ControllerException as e:
        print(e)
        return
    else:
        print('Selected Group:', device_manager.device.group.label)
        print('Selected Player:', device_manager.device.player_name)
        command_args = normalize_all_command_arguments(cli_manager.args)

        try:
            result = device_manager.perform_command(cli_manager.command, *command_args)
        except exc.BadCommandException as e:
            print(e)
            return

        if not isinstance(result, (str, unicode)):
            result_output = pprint.pformat(result)
        else:
            result_output = result
        print('{command}: {value}'.format(command=cli_manager.command, value=result_output))
