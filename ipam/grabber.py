#!/usr/bin/env python

'''
Author: Maurice Green
Usage:  IPAM CLI
'''

from ipam_main_class import url_obj
from collections import abc



state = True

class SubnetFeed(object):

    def __init__(self, fcd, select, param):

        if not isinstance(self._obj, abc.MutableSequence):
            raise StandardError("")
        self._obj = fcd

        SubnetFeed.getid(self._obj, select, param)
    
    @classmethod
    def getparam(cls, obj, param, select=None, pin=None):
        for subnet in self._obj['data']:
            if select is None:
                return subnet[param]
            if subnet[pin] == select:
                return subnet[param]

class Grabber(url_obj):

    def get_sections(self, token, section_choice=""):
        headers = [
            'Content-Length: 53',
            'Accept: */*',
            'Token: %s' % str(token)
        ]
        url = "https://linkto.server.local/api/johndoe/sections/"
        datablock = url_obj.quick_build(url)
        if section_choice != "ALL":
            return SubnetFeed(datablock, section_choice, 'name', 'id')[0]
        
        company_dcenters = SubnetFeed(datablock,'name')
        datacenter_ids = SubnetFeed(datablock,'id')

        name_constructors = [
            (str(server_type)+dc) for dc in company_dcenters
        ]
        return (company_dcenters, datacenter_ids, name_constructors)

    def get_subnets(self, token, dc_id):
        orig_URI = "https://linkto.server.local/api/{}/sections/{}/subnets/".format(
            self.user, dc_id
        )
        first_call_data = url_obj.quick_build(orig_URI)

        # Use the nested function above for easier recursion
        def decision(sub_selection):
            selection = sub_selection.strip()
            id_holder = SubnetFeed(first_call_data, 'id', select=selection, pin='subnet')[0]

            new_uri = "https://linkto.server.local/api/{}/subnets/{}/first_free/".format(
                self.user, id_holder
            )

            second_call_data = url_obj.quick_build(new_uri)

            # return (id_holder, second_call_data['data'])
            return second_call_data['data']
            
            url_obj.close()
        
        if not sys.argv[3] == "--list":
            sec_sub_id = SubnetFeed(first_call_data, 'id', select=sys.argv[3], pin='subnet')
            # print specific.  Just in case the subnet desired is already known

            id_holder = sec_sub_id

            new_uri = "https://linkto.server.local/api/{}/subnets/{}/first_free/".format(
                self.user, id_holder
            )

            second_call_data = url_obj.quick_build(new_uri, token_val=ipam_token, postfields=[])
            return (id_holder, second_call_data['data'])
            url_obj.close()


        selection = raw_input("Enter Subnet Selection (type 'continue' to print more):  ").strip()
        desclist = [
            (subnet['subnet'], subnet['mask'], subnet['description']) for subnet in first_call_data['data']
        ]

        while state:
            divider = len(desclist)/3

            while selection == "continue":
                (s, m, d) = [level for level in desclist[:divider:divider*2]]
                print (s, m, d)
                selection = raw_input("Enter Subnet Selection (type 'continue' to print more): ").strip()

            decision(selection)
