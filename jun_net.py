#!/usr/bin/env python

'''
Author: Maurice Green
Purpose: Scrap Juniper CAM table information (based on interface: Learned MAC and OUI Vendor
'''
from netmiko import ConnectHandler
from getpass import getpass
import re
import time
import pycurl
from StringIO import StringIO

class curlMAC():

        def __init__(self, mac):
                self.url = "http://api.macvendors.com/" + mac
                self.curl = pycurl.Curl()
                self.buffer = StringIO()
                self.curl.setopt(self.curl.HTTPGET, 1)
                self.curl.setopt(self.curl.URL, self.url)
                self.curl.setopt(self.curl.WRITEFUNCTION, self.buffer.write)
                self.curl.perform()
                self.vendor = self.buffer.getvalue()
                self.buffer.close()



class connectNet(object):
        results = ""
        def __init__(self, type, addr, user, passwd):
                self.type = type
                self.addr = addr
                self.user = user
                self.passwd = passwd
                #self.secret = secret_for_enable

                try:
                        # attempt to make connection
                        print "[*] Connecting to %s\n" % self.addr
                        self.connection = ConnectHandler(
                                device_type = self.type,
                                ip = self.addr,
                                username = self.user,
                                password = self.passwd,
                                session_timeout = 15
                                #secret = self.secret
                        )
                except:
                        print "Failed to Establish Connection!\n"

        def escalate(self):
                if not self.connection.check_enable_mode():
                        self.connection.enable()

        def configure(self, command_set):

                if not self.connection.check_config_mode():
                        try:
                                self.connection.config_mode()
                        except:
                                print "Failed to Enter Config Mode"

                while self.connection.check_config_mode():
                        self.connectoin.send_config_set(command_set)
                        # no indinite loops ;)
                        try:
                                self.connection.cleanup()
                        except:
                                print "Failed to gracefully exit, Now forcing exit!\n"
                                self.connection.exit_config_mode()

        def commands(self, command_set):
                
                start = time.time()
                '''
                if len(command_set) == 1:
                        results += self.connection.send_command(command_set[0], delay_factor=2.6)
                else:
                        results += self.connection.send_config_set(command_set)

                return results

                '''
                #print "\t[*] Execution Set[cmd]: %s" % command_set[0]
                results = self.connection.send_command(command_set)
                end = time.time()
                elapsed = (end-start)
                print "\t[*] Execution Complete[Elapsed Time]: %s seconds" % elapsed
                container = results.split()
                if len(container) > 16:
                        return container[17]
                else:
                        return "NULL"

        def end(self):
                self.connection.disconnect()
                print "[*] Connection Closed"


def parseData(username, password):
        results = {}
        commandsList = {}
        with open('juniper_ints.txt', 'r') as interfaces:
                for line in interfaces.readlines():
                        line = line.strip()
                        commandsList[line] = 'show ethernet-switching table interface %s' % line
                interfaces.close()
        junConn = connectNet('juniper_junos', '192.168.1.1', username, password)
        for interface, cmd in commandsList.iteritems():
                print "Executing command[%s]: %s" % (interface, cmd)
                try:
                        data = junConn.commands(cmd)
                        tmac = data
                        checkvendor = curlMAC(tmac)
                        results[interface] = [data, checkvendor.vendor]
                except:
                        print "[*] Interface %s Failed" % line
                        continue
        junConn.end() # close connection

        return results


def main():
        username = raw_input("Enter the Account Username: ")
        password = getpass()
        while username is None or password is None:
                username = raw_input("Enter the Account Username: ")
                password = getpass()
        dataset = parseData(username, password)
        with open('dataresults.txt', 'w+') as mactable:
                for interface, data in dataset.iteritems():
                        print "Adding: %s, %s" % (interface, data)
                        mactable.write("%s - %s\n" % (interface, data))
                mactable.close()

if __name__ == "__main__":
        main()
