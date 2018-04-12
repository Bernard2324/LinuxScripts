#!/usr/bin/env python

from netmiko import ConnectHandler
from getpass import getpass
import re
import time

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
                print "\t[*] Execution Set[cmd]: %s" % command_set
                results = self.connection.send_command(command_set[0], delay_factor=2.6)
                end = time.time()
                elapsed = (end-start)
                print "\t[*] Execution Complete[Elapsed Time]: %s seconds" % elapsed
                return results

        def end(self):
                self.connection.disconnect()
                print "[*] Connection Closed"


def parseData(username, password):
        dataLines = []
        destPrefix = {}
        panConn = connectNet('paloalto_panos', '1.1.1.1', username, password)
        cmdSet = ['show routing route']
        data = panConn.commands(cmdSet)
        panConn.end() # close connection
        fileH = open('pandata.txt', 'w+')
        fileH.write(data)
        fileH.close()
        with open('pandata.txt', 'r') as resultHandler:

                for line in resultHandler.readlines():
                        line = line.strip()
                        dataLines.append(line)
                resultHandler.close()

        
        # networkPattern = re.compile(r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\/[0-9]+')
        # nextHop = re.compile(r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}')
        if dataLines:
                for route in dataLines:
                        # I can use regex, however I can easily split the lines
                        # not the regex is and option if desired.
                        specs = []
                        try:
                                dest = route.split()[0]
                                specs.append(route.split()[1])
                                specs.append(route.split()[5])
                                if dest in destPrefix:
                                        print "skipping duplicte: %s" % dest
                                        continue

                                destPrefix[dest] = specs
                        except:
                                pass
                return destPrefix
        else:
                print "[Error]: No Data Collected!  You're not a very Good SysAdmin!\n"

if __name__ == "__main__":
        username = raw_input("Enter The Account Username: ")
        password = getpass()
        while username is None or len(password) == 0:
                username = raw_input("Enter The Account Username: ")
                password = getpass()
        dataset = parseData(username, password)
        print "\n\n"
        print dataset
