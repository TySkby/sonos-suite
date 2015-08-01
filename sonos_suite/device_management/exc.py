from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


class ControllerException(Exception):
    pass


class NoSearchResultsException(ControllerException):
    LIST_ITEM_SEPARATOR = '\n\t- '

    def __init__(self, error_message, list_label, list_items):
        self.error_message = error_message
        self.list_label = list_label
        self.list_items = list_items
        super(NoSearchResultsException, self).__init__(
            '{}.\n{}: {}{}'.format(
                error_message,
                list_label,
                self.LIST_ITEM_SEPARATOR,
                self.LIST_ITEM_SEPARATOR.join(list_items)
            )
        )


class NoDeviceSearchResultsException(NoSearchResultsException):
    def __init__(self, available_player_names):
        super(NoDeviceSearchResultsException, self).__init__(
            'No matching devices found',
            'Available player names',
            available_player_names
        )


class NoGroupSearchResultsException(NoSearchResultsException):
    def __init__(self, available_group_names):
        super(NoGroupSearchResultsException, self).__init__(
            'No matching groups found',
            'Available group names',
            available_group_names
        )


class BadCommandException(ControllerException):
    pass
