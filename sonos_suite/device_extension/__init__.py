# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import soco.config

from . import device


def apply_config_override():
    soco.config.SOCO_CLASS = device.SonosDevice
