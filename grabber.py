#!/usr/bin/env python

'''
Author: Maurice Green
Usage:  IPAM CLI
'''

from ipam_main_class import url_obj

class Grabber(url_obj):

    def __init__(self):
        url_obj.__init__(self)

    def get_token(self):
        fields = {'ipamusername': self.user, 'ipampassword': self.passwd}
        token_grab = 'https://linkto.server.local/api/%s/user/' % self.user
        datablock = url_obj.quick_build(token_grab, fields)
        ipam_token = datablock['data']['token']
        return ipam_token

    def get_sections(self, token, section_choice=""):
        headers = [
            'Content-Length: 53',
            'Accept: */*',
            'Token: %s' % str(token)
        ]
        url = "https://linkto.server.local/api/johndoe/sections/"
        datablock = url_obj.quick_build(url, token_val=token, postfields=[])
        if section_choice == "ALL":
            company_dcenters = [section['name'] for section in datablock['data']]
            datacenter_ids = [section['id'] for section in datablock['data']]
            name_constructors = [(str(server_type)+dc) for dc in company_dcenters]
            return (company_dcenters, datacenter_ids, name_constructors)
        else:
            target_id = [section['id'] for section in datablock['data'] if section['name'] == section_choice]
            return str(target_id[0])

    def get_subnets(self, token, dc_id):
        ipam_token = token
        orig_URI = "https://linkto.server.local/api/%s/sections/%s/subnets/" % (self.user, dc_id)
        first_call_data = url_obj.quick_build(orig_URI, token_val=ipam_token, postfields=[])
        # Use the nested function above for easier recursion
        def decision(sub_selection):
            selection = sub_selection.strip()
            sec_sub_id = [subnet['id'] for subnet in first_call_data['data'] if subnet['subnet'] == selection]
            id_holder = str(sec_sub_id[0])
            new_uri = "https://linkto.server.local/api/%s/subnets/%s/first_free/" % (self.user, id_holder)
            second_call_data = url_obj.quick_build(new_uri, token_val=ipam_token, postfields=[])
            # return (id_holder, second_call_data['data'])
            print "First Free IP Address For Selected Subet: %s" % second_call_data['data']
            url_obj.close()
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
            second_call_data = url_obj.quick_build(new_uri, token_val=ipam_token, postfields=[])
            return (id_holder, second_call_data['data'])
            url_obj.close()
