#!/usr/bin/env python
# Author: Maurice Green

import csv
from socket import gethostbyname


def quick_dns_check():
    csv_doc = 'splunk_forwarder_proj.csv'
    with open(csv_doc, 'rb') as dreader:
        host_reader = csv.reader(dreader, dialect='excel', delimiter=',')
        for row in host_reader:
            hostname = row[0] + ".splunk.domain.local"
            try:
                print "Host %s: %s" % (hostname, gethostbyname(hostname))
            except:
                from re import sub
                print "Host %s: Has No DNS Record!  Should Be %s" % (hostname,sub(r'eth0=', "",row[5]))
                continue
        dreader.close()
quick_dns_check()
