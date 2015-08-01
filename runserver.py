# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse

from sonos_suite.user_interfaces.web.application import serve


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('host', default='localhost')
    parser.add_argument('port', default=80)
    parser.add_argument('-d', '--debug', action='store_true', default=False)
    args = parser.parse_args()
    serve(args.host, int(args.port), args.debug)
