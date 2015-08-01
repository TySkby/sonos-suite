# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import falcon
import json

from sonos_suite.device_management.device_manager import SonosDeviceManager
from sonos_suite.device_management import exc as device_management_exc
from sonos_suite.user_interfaces.utils import normalize_all_command_arguments


def set_request_context_param_getter(req, resp, params):
    param_getter = req.get_param

    if req.method == 'POST':
        try:
            payload = json.load(req.stream, 'utf-8')
            param_getter = payload.get
            assert isinstance(payload, dict)
        except (ValueError, AssertionError):
            raise falcon.HTTPBadRequest(title='MALFORMED JSON', description="Couldn't decode the request body")

    req.context['param_getter'] = param_getter


@falcon.before(set_request_context_param_getter)
class DeviceCommandResponder(object):
    DEBUG_MODE = False

    def __init__(self, logger, debug_mode=False):
        self.logger = logger
        self.DEBUG_MODE = bool(debug_mode)

    def on_get(self, req, resp, command=None):
        if command is None:
            raise falcon.HTTPNotFound()

        result = self.get_result_for_requested_command(req, command)
        self.build_response_for_result(resp, result)

    def on_post(self, req, resp, command):
        if command is None:
            raise falcon.HTTPNotFound()

        result = self.get_result_for_requested_command(req, command)
        self.build_response_for_result(resp, result)

    def get_result_for_requested_command(self, request, command):
        device_manager = self._get_device_manager(request)
        command_arguments = self._get_command_arguments(request)

        try:
            result = self._get_command_result(device_manager, command, command_arguments)
        except Exception as e:
            if self.DEBUG_MODE:
                self.logger.exception(e)
                result = repr(e)
            else:
                raise

        return result

    def build_response_for_result(self, response, result):
        response.status = falcon.HTTP_OK
        if isinstance(result, (str, unicode)):
            response.body = result
        else:
            try:
                response.body = json.dumps(result)
            except TypeError as e:
                if self.DEBUG_MODE:
                    self.logger.exception(e)
                    response.body = repr(e)
                    response.status = falcon.HTTP_INTERNAL_SERVER_ERROR
                else:
                    raise

    def _get_device_manager(self, request):
        player_query, group_query = self._get_player_and_group_query_values(request)

        try:
            return SonosDeviceManager(player_name=player_query, group_name=group_query)
        except device_management_exc.NoSearchResultsException as e:
            raise falcon.HTTPNotFound(
                title=e.error_message,
                description='{label}: {items}'.format(label=e.list_label, items=', '.join(e.list_items))
            )

    def _get_player_and_group_query_values(self, request):
        player = self.get_request_param(request, 'player')
        group = self.get_request_param(request, 'group')

        if all([player, group]):
            raise falcon.HTTPBadRequest(
                'REQUEST ARGUMENT OVERLAP',
                'Only one of "player" or "group" may be specified'
            )

        if not any([player, group]):
            raise falcon.HTTPBadRequest(
                'MISSING REQUEST ARGUMENTS',
                'Cannot find a device without specifying either "player" or "group" query strings'
            )

        return player, group

    def _get_command_arguments(self, request):
        raw_arguments = self.get_request_param(request, 'args')
        if raw_arguments is not None:
            if isinstance(raw_arguments, (str, unicode)):
                return normalize_all_command_arguments(raw_arguments.split(','))
            elif isinstance(raw_arguments, (list, tuple)):
                return normalize_all_command_arguments(raw_arguments)
        return []

    @staticmethod
    def _get_command_result(device_manager, command, command_arguments):
        try:
            return device_manager.perform_command(command, *command_arguments)
        except device_management_exc.BadCommandException as e:
            raise falcon.HTTPNotFound(title='UNKNOWN COMMAND', description=e.message)

    @staticmethod
    def get_request_param(request, name):
        return request.context['param_getter'](name)
