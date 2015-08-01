from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import difflib

import soco

import sonos_suite.device_extension
from sonos_suite.device_management import exc


# Instruct soco to use our extended device rather than the native SoCo type
sonos_suite.device_extension.apply_config_override()

# Default attribute value for identifying a non-existent command
NO_COMMAND = object()


class SonosDeviceManager(object):
    def __init__(self, player_name=None, group_name=None):
        devices = self.get_device_list()

        if not devices:
            raise exc.ControllerException('No devices found')
        elif player_name is not None:
            self.device = self.find_device_by_player_name(devices, player_name)
        elif group_name is not None:
            self.device = self.find_coordinator_device_by_group_name(devices, group_name)
        else:
            self.device = devices[0]

    @classmethod
    def get_device_list(cls, retries_remaining=3):
        try:
            devices = list(soco.discover())
            assert len(devices) > 0
            return devices
        except (AssertionError, TypeError):
            if retries_remaining > 0:
                return cls.get_device_list(retries_remaining - 1)
            else:
                raise

    @classmethod
    def find_device_by_player_name(cls, devices, search_term):
        return cls.get_device_from_best_match_key(
            {d.player_name: d for d in devices},
            search_term,
            exc.NoDeviceSearchResultsException
        )

    @classmethod
    def find_coordinator_device_by_group_name(cls, devices, search_term):
        return cls.get_device_from_best_match_key(
            {gc.group.label: gc for gc in {d.group.coordinator for d in devices}},
            search_term,
            exc.NoGroupSearchResultsException
        )

    @staticmethod
    def get_device_from_best_match_key(search_dict, search_term, no_results_exception_class=None):
        possibilities = search_dict.keys()

        try:
            best_match = difflib.get_close_matches(search_term, possibilities, n=1, cutoff=0.1)[0]
        except IndexError:
            if issubclass(no_results_exception_class, exc.NoSearchResultsException):
                raise no_results_exception_class(possibilities)
            else:
                raise

        return search_dict[best_match]

    def perform_command(self, command_name, *args):
        device_command = getattr(self.device, command_name, NO_COMMAND)

        if device_command is NO_COMMAND:
            raise exc.BadCommandException('Unknown command: "{}"'.format(command_name))
        elif callable(device_command):
            command_result = device_command(*args)
            return command_result or 'successful'
        else:
            if args:
                setattr(self.device, command_name, *args)
            return getattr(self.device, command_name)
