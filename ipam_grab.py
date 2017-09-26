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

'''
Author: Maurice Green
argv2 = DC Abbreviation (as per IPAM)
argv3 = Description Name.  will accept regex bc this is iconsistent b/t DC's

'''

class url_obj(object):

    def __init__(self, os.environ['USER']):
        #threading.Thread.__init__(self)
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
        #self.curl.setopt(self.curl.VERBOSE, True)


    def get_token(self):
        token = re.compile('token:')
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

    def get_sections(self, token, section_choice):
        headers = [
            'Content-Length: 53',
            'Accept: */*',
            'Token: %s' % str(token)
        ]
        responseBuff = StringIO.StringIO()
        for header in headers:
            self.curl.setopt(self.curl.HTTPHEADER, [header])
        url = "https://linkto.server.local/api/%s/sections/" % self.user
        self.curl.setopt(self.curl.HTTPGET, 1)
        self.curl.setopt(self.curl.WRITEFUNCTION, responseBuff.write)
        self.curl.setopt(self.curl.URL, url)
        self.curl.perform()
        responseBuff.seek(0)
        data = json.loads(responseBuff.readlines()[0])
        target_id = [section['id'] for section in data['data'] if section['name'] == section_choice]
        return str(target_id[0])

    def get_subnets(self, token, dc_id):
        def build_curl(url_resource, token_value):
            responseBuff = StringIO.StringIO()
            headers = [
                'Content-Length: 53',
                'Accept: */*',
                'Token: %s' % str(token_value)
            ]
            for header in headers:
                self.curl.setopt(self.curl.HTTPHEADER, [header])
            self.curl.setopt(self.curl.HTTPGET, 1)
            self.curl.setopt(self.curl.WRITEFUNCTION, responseBuff.write)
            self.curl.setopt(self.curl.URL, url_resource)
            self.curl.perform()
            responseBuff.seek(0)
            data = json.loads(responseBuff.readlines()[0])
            return data
        # Use the nested function above for easier recursion
        orig_URI = "https://linkto.server.local/api/%s/sections/%s/subnets/" % (self.user, dc_id)
        first_call_data = build_curl(orig_URI, token)
        def decision(sub_selection):
            selection = sub_selection.strip()
            sec_sub_id = [subnet['id'] for subnet in first_call_data['data'] if subnet['subnet'] == selection]
            id_holder = str(sec_sub_id[0])
            new_uri = "https://linkto.server.local/api/%s/subnets/%s/first_free/" % (self.user, id_holder)
            second_call_data = build_curl(new_uri, token)
            print "First Free IP Address For Selected Subet: %s" % second_call_data['data']
            self.curl.close()
        if sys.argv[3] == "--list":
            # print list of subnets and desctriptions
            desclist = [(subnet['subnet'], subnet['mask'], subnet['description']) for subnet in first_call_data['data']]
            print "\t\t ------------ Subnet/Mask ---------- \t Description -------------\n"
            state = True
            while state:
                divider = len(desclist)/3
                for level in desclist[:divider]:
                    (subnet, mask, desc) = level
                    print "\t\t %s/%s -------- %s" % (subnet, mask, desc)
                selection = raw_input("Enter Subnet Selection (type 'continue' to print more):  ")
                selection = selection.strip()
                if selection == "continue":
                    for level in desclist[divider:divider*2]:
                        (subnet, mask, desc) = level
                        print "\t\t %s/%s -------- %s" % (subnet, mask, desc)
                    selection = raw_input("Enter Subnet Selection (type 'continue' to print more):  ")
                    selection = selection.strip()
                    if selection == "continue":
                        for level in desclist[divider*2:]:
                            (subnet, mask, desc) = level
                            print "\t\t %s/%s -------- %s" % (subnet, mask, desc)
                        selection = raw_input("Enter Subnet Selection (Type: 'Ctrl + C' To Cancel):  ")
                        selection = selection.strip()
                        decision(selection)
                        state = False
                    else:
                        decision(selection)
                        state = False
                else:
                    decision(selection)
                    state = False
        else:
            # print specific.  Just in case the subnet desired is already known
            sec_sub_id = [subnet['id'] for subnet in first_call_data['data'] if subnet['subnet'] == str(sys.argv[3])]
            id_holder = str(sec_sub_id[0])
            new_uri = "https://linkto.server.local/api/%s/subnets/%s/first_free/" % (self.user, id_holder)
            second_call_data = build_curl(new_uri, token)
            print "First Free IP Address For Selected Subet: %s" % second_call_data['data']
            self.curl.close()

if __name__ == "__main__":
    ipam = url_obj()
    token = ipam.get_token()
    dc = ipam.get_sections(token, sys.argv[2])
    ipam.get_subnets(token, dc)
