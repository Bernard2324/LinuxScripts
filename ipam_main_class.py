#!/usr/bin/env python

'''
Author: Maurice Green
Usage:  IPAM CLI
'''

from urllib import urlencode
import threading
import StringIO
import json
import pycurl
import getpass
import re
import sys
import os

class url_obj(object):

    def __init__(self):
        #threading.Thread.__init__(self)
        headers = [
            'Content-Length: 53'
        ]
        self.user = os.environ['USER']
        print "Please Enter Your AD Password for: %s\n" % self.user
        self.passwd = getpass.getpass()
        self.curl = pycurl.Curl()
        self.curl.setopt(self.curl.POST, 1)
        self.curl.setopt(self.curl.CONNECTTIMEOUT, 60)
        self.curl.setopt(self.curl.TIMEOUT, 15)
        self.curl.setopt(self.curl.SSL_VERIFYPEER, 0)
        self.curl.setopt(self.curl.SSL_VERIFYHOST, 0)
        for header in headers:
            self.curl.setopt(self.curl.HTTPHEADER, [header])
        if self.user is not None:
            print "\nSetting IPAM credentials for User: %s" % self.user
            self.curl.setopt(self.curl.USERPWD, '%s:%s' % (self.user, self.passwd))
        #### optional Verbosity, thurn this on for debugging ###
        #self.curl.setopt(self.curl.VERBOSE, True)

    def quick_build(self, resource, token_val=None, postfields):
        writeBuffer = StringIO.StringIO()
        if token_val is not None:
            headers = [
                'Content-Length: 53',
                'Accept: */*',
                'token: %s' % token_val
            ]
            for header in headers:
                self.curl.setopt(self.curl.HTTPHEADER, [header])
        else:
            # NOOP
            pass
        self.curl.setopt(self.curl.URL, resource)
        if postfields is not None:
            # must pass the dictionary as the postfields parameter: {'user':user123, 'pass':'abc123'}
            parameters = urlencode(postfields)
            self.curl.setopt(self.curl.POSTFIELDS, parameters)
        else:
            # I suppose I'll just pass empty array:  quick_build('http://url.com', 'token123adagv', emptyarray=[])
            self.curl.setopt(self.curl.HTTPGET, 1)
        self.curl.setopt(self.curl.TIMEOUT, 15)
        self.curl.setopt(self.curl.WRITEFUNCTION, writeBuffer.write)
        self.curl.perform()
        writeBuffer.seek(0)
        dataOutput = json.loads(writeBuffer.readlines()[0])
        return dataOutput

    def close(self):
        self.curl.close()
