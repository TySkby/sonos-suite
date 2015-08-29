from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

import falcon
from wsgiref import simple_server

from sonos_suite.user_interfaces.web.responders import DeviceCommandResponder


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


def make_app(debug=False):
    app = falcon.API()
    device_responder = DeviceCommandResponder(logger, debug_mode=debug)
    app.add_route('/sonos-server/{command}', device_responder)
    return app


def serve(host='localhost', port=80, debug=False):
    httpd = simple_server.make_server(
        host=host,
        port=port,
        app=make_app(debug)
    )
    logger.info('* Running on http://%s:%s/', httpd.server_address)
    if debug:
        logger.info('* Running in DEBUG mode')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.warning('\nShutting down...')
        httpd.shutdown()
