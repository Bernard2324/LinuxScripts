#!/usr/bin/env python
# This is a work in progress, and does not work at the moment.
# Author: Maurice Green

import pymysql
import sys, re, os
import threadin.Thread
import getpass
from ConfigParser import *

class db_insert(threading.Thread):
    def __init__(self, username, dbname='nagios'):
        threading.Thread.__init__(self)
        self.user = username
        self.password = getpass.getpass()
        self.db = dbname
        self.connect = pymysql.connect(self.user, self.password, self.db, unix_socket='/var/run/mysql/mysql.sock')
        self.curs = self.connect.cursor()
        self.start()

    def insert_services(self, host, ip, services=None, Interval=None):
        services = [str(srv) for srv in services if self.__isNotPresent(host, srv)]
        print "Beginning Service Insertion..."
        print "Inserting %r Services!" % len(services)
        count = len(services)
        while count >= 1:
            
            _insertionQ = """
                INSERT INTO services (host_name, host_ip, service_description, interval) VALUES \
                (%s, %s, %s, %s)
            """ % (host, ip, services[count-1], Interval[count-1])
            count -= 1
            try:
                self.curs.execute(_insertionQ)
                self.connect.commit()
            else:
                print "Commit Failed on Service: %s" % services[count-1]
                self.connect.rollback()
        


    def __isNotPresent(self, host, service):
        check_serice = "SELECT %s FROM services WHERE host_name=%s" % (service, host)
        self.curs.execute(check_service)
        value = self.connect.commit()
        if value:
            return False
        else:
            return True

    def insert_host(self, host, ip):
        _insertionQ = """
            INSERT INTO hosts (host_name, ipaddr) VALUES \
            (%s, %s);
        """ % (host, ip)
        print "Attempting to Add Host: %s" % host
        try:
            self.curs.execute(_insertionsQ)
            self.connect.commit()
        except:
            print "Failed To Add Host: %s" % host
            print "This script Will Exit Because We cannot add Services With the Corresponding Host Entry"
            sys.exit(1)
        

def __configGrabber():
    location = '/home/%s' % os.environ['USER']
    holder = {}
    for file in os.listdir(location):
        if file.endswith('.nagios'):
            print "Extracting Nagios Information From %s" % file
            config = RawConfigParser()
            try:
                config.read()
            else:
                pass
            holder['host'] = config.get('host', 'hostname')
            holder['ip'] = config.get('host', 'hostip')
            holder['services'] = [config.get('service:description', option) for option in config.options('service:desciption')]
            holder['interval'] = [config.get('service:interval', option) for option in config.options('service:interval')]
        else:
            continue
    print "Feeding Data"
    db = db_insert('%s') % os.environ['USER']
    db.insert_host(holder['host', holder['ip']])
    db.insert_services(holder['host'], holder['ip'], holder['services'] holder['interval'])

if __name__ == "__main__":
    __configGrabber()
    
