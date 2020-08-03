# -*- coding: utf-8 -*-

import io, os, sys, datetime
import picamera
import socketserver
from threading import Condition
from http import server
sys.path.append('/home/pi/git/pi') # for running from command line.
from modules.common import LOGGER, CONFIGURATION, timestamp
import base64
from modules.send_email import sendMail
from time import sleep

PAGE="""\
<html>
<head>
<title>shrimp camera</title>
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
        if auth != "Basic %s" % base64.b64encode((p.camera.LOGIN + ':'+ p.camera.PASS).encode()).decode():
            self.send_response(401)
            self.send_header("WWW-Authenticate", 'Basic realm="webiopi"')
            self.end_headers();
            logger.error('no auth')
            return False
        logger.debug('auth OK')
        return True

    def do_GET(self):
        #no auth for alert
        if self.path == '/alert':
            self.send_response(200)
            with CM(resolution='{}x{}'.format(p.camera.X, p.camera.Y), framerate=p.camera.R) as camera:
                f1 = camera.Capture(p.camera.PATH)
                v1 = camera.Record(p.camera.PATH, p.camera.RECORD)
                f2 = camera.Capture(p.camera.PATH)

            logger.info('sending email ... ' + sendMail([p.email.address],
                                                        [p.email.address, p.email.login, p.email.password],
                                                        'motion detected',
                                                         str(datetime.datetime.now()).split('.')[0]+ '\n' +
                                                         'video file: '+ v1,
                                                        [f1, f2]))
            return

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
                with CM(resolution='{}x{}'.format(p.camera.X, p.camera.Y), framerate=p.camera.R) as camera:
                    camera.Stream()
                    logger.info('start streaming : %s', self.client_address )
                    os.system("curl hornet.local:8083/cmnd?RUN=CAMERA_ON")
                    while True:
                        with camera.output.condition:
                            camera.output.condition.wait()
                            frame = camera.output.frame
                        self.wfile.write(b'--FRAME\r\n')
                        self.send_header('Content-Type', 'image/jpeg')
                        self.send_header('Content-Length', len(frame))
                        self.end_headers()
                        self.wfile.write(frame)
                        self.wfile.write(b'\r\n')
            except Exception as e:
                logger.error(str(e))

                logger.info('stop streaming')
                os.system("curl hornet.local:8083/cmnd?RUN=CAMERA_OFF")
                logger.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
            finally:
                try:
                    camera.camera.stop_recording()
                    del camera
                except:
                    logger.error('camera element already removed - OK ')

        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

class CM(picamera.PiCamera):
    def __init__(self, *args,  **kwargs):
        super().__init__(*args, **kwargs)
        sleep(1)
    # def __init__(self, x, y, r, path): #p.camera.X, p.camera.Y, p.camera.R, p.camera.PATH
    #     self.camera = picamera.PiCamera(resolution='{}x{}'.format(x, y), framerate=r)
    #     self.path = path
    def Capture(self, path):
        f = os.path.join(path, timestamp())+'.jpeg'
        logger.info('saving picture %s', f)
        self.capture(f)
        return  f
    def Record(self, path, time=10): #p.camera.RECORD
        f = os.path.join(path, timestamp())+'.h264'
        logger.info('saving video %s', f)
        self.start_recording(f)
        self.wait_recording(time)
        self.stop_recording()
        logger.info('recording stopped')
        return f
    def Stream(self):
        self.output = StreamingOutput()
        self.start_recording(self.output, format='mjpeg')

if __name__ == '__main__':
    logger = LOGGER('camera_stream', 'INFO', True)
    p = CONFIGURATION() #LOGIN:PASS
    PAGE = PAGE.format(p.camera.X, p.camera.Y)

    try:
        logger.info('start camera ')
        address = ('', 8000)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
    finally:
        logger.info('stop camera')
        #camera.stop_recording()