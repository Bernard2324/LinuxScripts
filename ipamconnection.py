from urllib import urlencode
import pycurl
import StringIO
import os
import re
import json
import getpass

class UrlMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in _instances:
            _instances[cls] = super(UrlMeta, cls).__call__(*args, **kwargs)
        return _instances[cls]

class IpamConnection(object):

    __metaclass__ = UrlMeta


    def __init__(self):
        
        self.headers = {
            'content-Length:': '53'
        }

        self.user = os.environ['USER']
        print "Please Enter Your AD Password for: %s\n" % self.user
        self.passwd = getpass.getpass()
        self.curl = pycurl.Curl()
        opts = {
            self.curl.POST: 1,
            self.curl.CONNECTTIMEOUT: 60,
            self.curl.TIMEOUT: 15,
            self.curl.SSL_VERIFYPEER: 0,
            self.curl.SSL_VERIFYHOST: 0
        }

        for k, v in opts:
            self.curl.setopt(k, v)

        for k, v in headers:
            self.curl.setopt(self.curl.HTTPHEADER, ["".join(k, v)])
        
        if self.user is not None:
            self.curl.setopt(self.curl.USERPWD, '%s:%s' % (self.user, self.passwd))
    
    def close(self):
        self.curl.close()

class ConnectionAction(IpamConnection):

    def __init__(self, sheaders=None):
        super(ConnectionAction, self).__init__()

        if sheaders is not None:
            self.header.update(sheaders)

    def gather(self, *args, **kwargs):
        responseBuffer = StringIO.StringIO()

        if not all(i in kwargs for i in args):
            raise('')

        if 'postfields' in kwargs:
            params = urlencode(kwargs['postfields'])
            self.curl.setopt(self.curl.POSTFIELDS, params)

        for i in args:
            self.curl.setopt(self.curl.i, kwargs[i])

        self.curl.perform()
        responseBuffer.seek(0)

        return json.loads(responseBuffer.readlines()[0])[kwargs['data']][kwargs['set']]
