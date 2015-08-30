from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import unittest

import falcon

from sonos_suite.user_interfaces.web import application
from sonos_suite.user_interfaces.web import responders


class ApplicationLoggerTestCase(unittest.TestCase):
    def test_logger_name(self):
        self.assertEqual(application.logger.name, application.__name__)

    def test_logger_level(self):
        self.assertEqual(application.logger.level, logging.INFO)

    def test_logger_handlers(self):
        self.assertEqual(len(application.logger.handlers), 1)
        self.assertIsInstance(application.logger.handlers[0], logging.StreamHandler)


class ApplicationMakeAppTestCase(unittest.TestCase):
    def test_returns_falcon_app(self):
        self.assertIsInstance(application.make_app(), falcon.API)

    def test_responder_configuration(self):
        expected_number_of_routes = 1
        app = application.make_app()
        self.assertEqual(len(app._router._return_values), expected_number_of_routes)
        resource = app._router.find('/sonos-server/test-command')[0]
        self.assertIsInstance(resource, responders.DeviceCommandResponder)

    def test_responder_debug_mode_configuration_default_value(self):
        app = application.make_app()
        resource = app._router.find('/sonos-server/test-command')[0]
        self.assertFalse(resource.DEBUG_MODE)

    def test_responder_debug_mode_is_same_as_make_app_debug_mode(self):
        self.assertFalse(application.make_app(debug=False)._router.find('/sonos-server/test-command')[0].DEBUG_MODE)
        self.assertTrue(application.make_app(debug=True)._router.find('/sonos-server/test-command')[0].DEBUG_MODE)


class ApplicationServeTestCase(unittest.TestCase):
    # TODO
    pass





