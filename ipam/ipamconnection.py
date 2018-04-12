import os
import pycurl
import StringIO
import json
import getpass
from urllib import urlencode


class UrlMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(UrlMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class IpamConnection(object):

    __metaclass__ = UrlMeta

    def __init__(self, sheaders=None):
        
        self.headers = {
            'content-Length:': '53'
        }
        
        self.user = os.environ['USER']
        self.passwd = getpass.getpass("Enter Password For \({}\)".format(self.user))
        self.curl = pycurl.Curl()
        
        self._opts = {
	        "self.curl.POST": 1,
	        "self.curl.CONNECTTIMEOUT": 60,
	        "self.curl.TIMEOUT": 15,
	        "self.curl.SSL_VERIFYPEER": 0,
	        "self.curl.SSL_VERIFYHOST": 0
        }

        for k, v in self._opts.items():
            self.curl.setopt(k, v)
        
        self.curl.setopt(pycurl.HTTPHEADER, ["".join([k, v]) for k, v in self.headers.items()])
        
        if self.user is not None:
            self.curl.setopt(pycurl.USERPWD, '%s:%s' % (self.user, self.passwd))


class ConnectionAction(IpamConnection):

    def __init__(self, sheaders=None):
        super(ConnectionAction, self).__init__()
        
        if sheaders is not None:
            self.headers.update(sheaders)

    def gather(self, *args, **kwargs):
        responsebuffer = StringIO.StringIO()

        if not all(i in kwargs for i in args):
            raise ValueError('Missing Arguments in KWARGS\n')

        if 'POSTFIELDS' in kwargs:
            params = urlencode(kwargs['POSTFIELDS'])
            self.curl.setopt(pycurl.POSTFIELDS, params)

        for i in args:
            self.curl.setopt(pycurl.i, kwargs[i])

        self.curl.perform()
        responsebuffer.seek(0)

        return json.loads(responsebuffer.readlines()[0])[kwargs['data']][kwargs['set']]
