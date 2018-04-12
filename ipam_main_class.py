#!/usr/bin/env python

'''
Author: Maurice Green
Usage:  IPAM CLI
'''

from ipamconnection import IpamConnection, ConnectionAction


class url_obj(object):

    def quick_build(self, resource, postfields):
        headers = {'Accept:': '*/*','token:': token_val}

        opts = {
            'HTTPGET': 1, 'TIMEOUT': 15, 'URL': resource
        }

        x = ConnectionAction(headers)
        return x.gather(*['HTTPGET', 'TIMEOUT', 'URL'], **opts)

    def close(self):
        self.curl.close()
