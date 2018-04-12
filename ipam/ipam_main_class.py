#!/usr/bin/env python

'''
Author: Maurice Green
Usage:  IPAM CLI
'''

from ipamconnection import IpamConnection, ConnectionAction

class UrlObj(object):
	_token = ""
	
	@classmethod
	def get_token(cls):
		c = IpamConnection()
		URI = 'https://ipam.example.com/api/{}/user/'.format(c.user)
		credentials = {'ipamusername': c.user, 'ipampassword': c.passwd}
		headers = {'Accept:': '*/*', 'Content-Length:': '53'}
		
		opts = {
			'TIMEOUT': 15, 'URL': URI, 'POSTFIELDS': credentials
		}
		
		x = ConnectionAction(headers)
		cls._token = x.gather(*['TIMEOUT', 'POSTFIELDS', 'URL'], **opts)
		
	@classmethod
	def quick_build(cls, resource, postfields):
		headers = {'Accept:': '*/*','token:': cls._token}
		opts = {'HTTPGET': 1, 'TIMEOUT': 15, 'URL': resource}
		
		x = ConnectionAction(headers)
		return x.gather(*['HTTPGET', 'TIMEOUT', 'URL'], **opts)\
		
	@classmethod
	def add_entry(cls, resource, hostname, desc, owner):
		headers = {'Accept:': '*/*', 'token:': cls._token}
		address_values = {
			'dns_name': hostname, 'description': desc, 'owner': owner
		}
		
		opts = {'URL': resource, "POSTFIELDS": address_values}
		
		x = ConnectionAction(headers)
		return x.gather(*['URL'], **opts)
