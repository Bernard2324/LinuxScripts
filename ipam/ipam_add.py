#!/usr/bin/env python

from urllib import urlencode
import threading
import StringIO
import json
import pycurl
import getpass
import ssl
import re
import sys

class url_obj(object):

    def __init__(self, username=os.environ['USER'], ipaddr, target_id):
        #threading.Thread.__init__(self)
        self.ipaddress = ipaddr
        self.id = target_id
        headers = [
            'Content-Length: 53'
        ]
        self.user = username
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
        self.curl.setopt(self.curl.VERBOSE, True)
    def get_token(self):
        fields = {'ipamusername': self.user, 'ipampassword': self.passwd}
        params = urlencode(fields)
        token_grab = 'https://linkto.server.local/api/%s/user/' % self.user
        responseBuff = StringIO.StringIO()
        self.curl.setopt(self.curl.URL, token_grab)
        self.curl.setopt(self.curl.POSTFIELDS, params)
        self.curl.setopt(self.curl.TIMEOUT, 15)
        self.curl.setopt(self.curl.WRITEFUNCTION, responseBuff.write)
        self.curl.perform()
        #self.curl.close()
        responseBuff.seek(0)
        parsed = json.loads(responseBuff.readlines()[0])
        ipam_token = parsed['data']['token']
        return ipam_token

    def add_entry(self, token, hostname, description):
        stringbuffer = StringIO.StringIO()
        headers = [
            'Content-Length: 53',
            'Accept: */*',
            'token: %s' % str(token)
        ]
        for header in headers:
            self.curl.setopt(self.curl.HTTPHEADER, [header])
        URI = "https://linkto.server.local/api/%s/addresses/1234/" % self.user
        address_values = {
            'dns_name': hostname,
            'description': description,
            'owner': 'ownership_name'
        }
        post_parameters = urlencode(address_values)
        self.curl.setopt(self.curl.URL, URI)
        self.curl.setopt(self.curl.POSTFIELDS, post_parameters)
        self.curl.setopt(self.curl.WRITEFUNCTION, stringbuffer.write)
        self.curl.perform()
        self.curl.close()
        stringbuffer.seek(0)
        print stringbuffer.readlines()


start = url_obj('192.168.1.1', '1111')
token = start.get_token()
start.add_entry(token, 'api.someserver.local', 'testapi-eth0')
