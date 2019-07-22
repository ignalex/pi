"""An example of how to setup and start an Accessory.

This is:
1. Create the Accessory object you want.
2. Add it to an AccessoryDriver, which will advertise it on the local network,
    setup a server to answer client queries, etc.
"""
#import logging
import signal
import socket 
import os
os.chdir('/home/pi/git/pi/accessories_ai')

import sys 
sys.path.append('/home/pi/git/pi') # for running from command line.
from modules.common import   MainException, LOGGER, CONFIGURATION

logger = LOGGER('camera', 'DEBUG', True)


from pyhap.accessory_driver import AccessoryDriver
from pyhap import camera

#logging.basicConfig(level=logging.DEBUG, format="[%(module)s] %(message)s")


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
            [1024, 768, 30],
            [640, 480, 30],
            [640, 360, 30],
            [480, 360, 30],
            [480, 270, 30],
            [320, 240, 30],
            [320, 180, 30],
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
    "address": socket.gethostbyname(socket.gethostname()), #"192.168.1.7", 
    "start_stream_cmd" : ('ffmpeg -f video4linux2 -input_format h264 -video_size {width}x{height} '
        '-framerate 20 -i /dev/video0 '
        '-vcodec copy -an -payload_type 99 -ssrc 1 -f rtsp '
        '-b:v {v_max_bitrate}k -bufsize {v_max_bitrate}k '
        '-payload_type 99 -f rtp '
        '-srtp_out_suite AES_CM_128_HMAC_SHA1_80 -srtp_out_params {v_srtp_key} '
        'srtp://{address}:{v_port}?rtcpport={v_port}&'
        'localrtcpport={v_port}&pkt_size=1378')
}

logger.debug('options: '+ str(options))
# Start the accessory on port 51826
driver = AccessoryDriver(port=51826)
acc = camera.Camera(options, driver, "Camera")
driver.add_accessory(accessory=acc)

# We want KeyboardInterrupts and SIGTERM (terminate) to be handled by the driver itself,
# so that it can gracefully stop the accessory, server and advertising.
signal.signal(signal.SIGTERM, driver.signal_handler)
# Start it!
driver.start()
