#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 26 10:04:56 2020

@author: alexander
"""

"""An example of how to setup and start an Accessory.

This is:
1. Create the Accessory object you want.
2. Add it to an AccessoryDriver, which will advertise it on the local network,
    setup a server to answer client queries, etc.
"""

import os
os.chdir('/home/pi/git/pi/accessories_ai')

import sys
sys.path.append('/home/pi/git/pi') # for running from command line.
from modules.common import LOGGER

from accessories_ai.start_stream_cmd import FFMPEG_CMD

logger = LOGGER('hap_camera', 'INFO', True)

import signal
from pyhap.accessory_driver import AccessoryDriver
from pyhap import camera, util


# Specify the audio and video configuration that your device can support
# The HAP client will choose from these when negotiating a session.
options = {
    "video": {
        "codec": {
            "profiles": [
                camera.VIDEO_CODEC_PARAM_PROFILE_ID_TYPES["BASELINE"],
                camera.VIDEO_CODEC_PARAM_PROFILE_ID_TYPES["MAIN"],
                camera.VIDEO_CODEC_PARAM_PROFILE_ID_TYPES["HIGH"]
            ],
            "levels": [
                camera.VIDEO_CODEC_PARAM_LEVEL_TYPES['TYPE3_1'],
                camera.VIDEO_CODEC_PARAM_LEVEL_TYPES['TYPE3_2'],
                camera.VIDEO_CODEC_PARAM_LEVEL_TYPES['TYPE4_0'],
            ],
        },
        "resolutions": [
            # Width, Height, framerate
            [320, 240, 15], # Required for Apple Watch
            [1296, 972, 30],
            [1296, 730, 30],
            [1280, 720, 30],
            # [640, 480, 30],
            # [1024, 768, 30],
            # [640, 480, 30],
            # [640, 360, 30],
            # [480, 360, 30],
            # [480, 270, 30],
            # [320, 240, 30],
            # [320, 180, 30],
        ],
    },
    "audio": {
        "codecs": [
            {
                'type': 'OPUS',
                'samplerate': 24,
            },
            {
                'type': 'AAC-eld',
                'samplerate': 16
            }
        ],
    },
    "srtp": True,

    # hard code the address if auto-detection does not work as desired: e.g. "192.168.1.226"
    "address": util.get_local_address(),
    "start_stream_cmd"   : FFMPEG_CMD
}


# Start the accessory on port 51826
driver = AccessoryDriver(port=51826)
acc = camera.Camera(options, driver, "Camera")
driver.add_accessory(accessory=acc)

# We want KeyboardInterrupts and SIGTERM (terminate) to be handled by the driver itself,
# so that it can gracefully stop the accessory, server and advertising.
signal.signal(signal.SIGTERM, driver.signal_handler)
# Start it!
driver.start()