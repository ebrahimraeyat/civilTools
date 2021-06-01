import os
import sys
import base64
import subprocess
from pathlib import Path


class CheckLegal:

    def __init__(self,
                filename,
                gist_url,
                dir_name='cfactor'
                ):
        appdata_dir = Path(os.getenv('APPDATA'))
        civiltoos_dir = appdata_dir / 'civiltools'
        if not civiltoos_dir.exists():
            civiltoos_dir.mkdir()
        cfactor_dir = civiltoos_dir / dir_name
        if not cfactor_dir.exists():
            cfactor_dir.mkdir()
        self.filename = cfactor_dir / filename
        self.gist_url = gist_url

    def allowed_to_continue(self):
        if sys.platform == "win32":
            if not self.is_registered:
                if not internet():
                    return False, 'INTERNET'
                serial = str(subprocess.check_output("wmic csproduct get uuid")).split("\\r\\r\\n")[1].split()[0]
                if not self.serial_number(serial):
                    return False, 'SERIAL'
                else:
                    self.register()
                    return True, 'REGISTERED'
            return True, ''
        return True, ''

    def initiate(self):
        with open(self.filename, 'wb') as f:
            b = base64.b64encode('0-0'.encode('utf-8'))
            f.write(b)

    @property
    def is_registered(self):
        if not Path(self.filename).exists():
            self.initiate()
            return True
        else:
            text = self.get_registered_numbers()
            if text[0] == 1 or text[1] <= 2:
                return True
            else:
                return False

    def get_registered_numbers(self):
        if not Path(self.filename).exists():
            return False
        with open(self.filename, 'rb') as f:
            b = f.read()
            text = base64.b64decode(b).decode('utf-8').split('-')
            return int(text[0]), int(text[1])

    def add_using_feature(self):
        if  Path(self.filename).exists():
            with open(self.filename, 'rb') as f:
                b = f.read()
                text = base64.b64decode(b).decode('utf-8').split('-')
                text[1] += 1
                text = '-'.join(*[text])
            with open(self.filename, 'wb') as f:
                b = base64.b64encode(text.encode('utf-8'))
        return

    def register(self):
        if  Path(self.filename).exists():
            with open(self.filename, 'rb') as f:
                b = f.read()
                text = base64.b64decode(b).decode('utf-8').split('-')
                text[0] = 1
                text = '-'.join(*[text])
            with open(self.filename, 'wb') as f:
                b = base64.b64encode(text.encode('utf-8'))

    def serial_number(self, serial):
        import urllib.request
        response = urllib.request.urlopen(self.gist_url)
        data = response.read()      # a `bytes` object
        text = data.decode('utf-8')
        return serial in text

def internet(host="8.8.8.8", port=53, timeout=3):
    import socket
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception as ex:
        #         print(ex.message)
        return False
