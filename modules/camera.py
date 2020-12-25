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
import requests

PAGE="""\
<html>
<head>
<title>shrimp camera</title>
</head>
<body>
<img src="stream.mjpg" width="{}" height="{}" />
{}
</body>
</html>
"""
SCRIPT = """<br>

    <button type="submit"  onClick="httpGet('move+20')"> << </button> &nbsp &nbsp
    <button type="submit"  onClick="httpGet('move-20')"> >> </button>
<script>
function httpGet(theUrl)
{
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open( "GET", 'move'+theUrl, false ); // false for synchronous request
    xmlHttp.send( null );
    //window.location.reload();
    //return xmlHttp.responseText;
};
</script>"""

WAIT = 1

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
            with CM(resolution='{}x{}'.format(p.camera.X, p.camera.Y), framerate=p.camera.R, path=p.camera.PATH) as camera:
                sleep(WAIT)
                f1 = camera.Capture()
                v1 = camera.Record(p.camera.RECORD)
                f2 = camera.Capture()

            logger.info('sending email ... ' + sendMail([p.email.address],
                                                        [p.email.address, p.email.login, p.email.password],
                                                        'motion detected',
                                                         str(datetime.datetime.now()).split('.')[0]+ '\n' +
                                                         'video file: '+ v1,
                                                        [f1, f2]))
            del camera
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
        elif self.path.startswith('/move'):
            "/move-100, /move+50"
            params = self.path.replace('/move','')
            requests.get('http://192.168.1.175/control/motor/{}'.format(params))
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                with CM(resolution='{}x{}'.format(p.camera.X, p.camera.Y), framerate=p.camera.R, path=p.camera.PATH) as camera:
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
                #logger.error(str(e))
                logger.info('stop streaming')
                os.system("curl hornet.local:8083/cmnd?RUN=CAMERA_OFF")
                logger.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
            finally:
                try:
                    # camera.stop_recording()
                    del camera
                except Exception as e:
                    logger.error('camera element already removed - OK - %s',  str(e))

        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

class CM(picamera.PiCamera):
    def __init__(self, *args,  **kwargs):
        super().__init__(*args, **{k:v for k,v in kwargs.items() if k not in ['path']})
        self.path = kwargs['path']
    def Capture(self):
        f = os.path.join(self.path, timestamp())+'.jpeg'
        logger.info('saving picture %s', f)
        self.capture(f)
        return  f
    def Record(self, time=10): #p.camera.RECORD
        f = os.path.join(self.path, timestamp())+'.h264'
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
    logger = LOGGER('camera', 'INFO', True)
    p = CONFIGURATION() #LOGIN:PASS
    PAGE = PAGE.format(p.camera.X, p.camera.Y, SCRIPT)

    try:
        logger.info('start camera ')
        address = ('', 8000)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
    finally:
        logger.info('stop camera')
        #camera.stop_recording()
