# -*- coding: utf-8 -*-

import io, os, sys
import picamera
import socketserver
from threading import Condition
from http import server
sys.path.append('/home/pi/git/pi') # for running from command line.
from modules.common import LOGGER, CONFIGURATION
import base64


PAGE="""\
<html>
<head>
<title>shrip camera</title>
</head>
<body>
<img src="stream.mjpg" width="{}" height="{}" />
</body>
</html>
"""


class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):

    def checkAuthentication(self):
        auth = self.headers.get('Authorization')
        if auth != "Basic %s" % base64.b64encode((p.LOGIN + ':'+ p.PASS).encode()).decode():
            self.send_response(401)
            self.send_header("WWW-Authenticate", 'Basic realm="webiopi"')
            self.end_headers();
            logger.error('no auth')
            return False
        logger.debug('auth OK')
        return True

    def do_GET(self):
        if not self.checkAuthentication():
            return

        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                camera.start_recording(output, format='mjpeg')
                logger.info('start streaming : %s', self.client_address )
                os.system("curl hornet.local:8083/cmnd?RUN=CAMERA_ON")
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                camera.stop_recording()
                logger.info('stop streaming')
                os.system("curl hornet.local:8083/cmnd?RUN=CAMERA_OFF")
                logger.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))

        else:
            self.send_error(404)
            self.end_headers()
class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


if __name__ == '__main__':
    logger = LOGGER('camera_stream', 'INFO', True)
    p = CONFIGURATION().camera #LOGIN:PASS
    X,Y = p.X, p.Y
    PAGE = PAGE.format(X,Y)

    with picamera.PiCamera(resolution='{}x{}'.format(X,Y), framerate=24) as camera:
        output = StreamingOutput()
        # camera.start_recording(output, format='mjpeg')
        try:
            logger.info('start camera ')
            address = ('', 8000)
            server = StreamingServer(address, StreamingHandler)
            server.serve_forever()
        finally:
            logger.info('stop camera')
            camera.stop_recording()