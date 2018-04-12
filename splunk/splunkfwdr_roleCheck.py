#!/usr/bin/env python
#Author: Maurice Green

import paramiko
#import commands
import socket
from getpass import getpass
from re import match, sub
from os import environ, path
from csv import reader
from socket import gethostbyaddr, gethostbyname

class SSH():
    def __init__(self, password, host, username=environ['USER']):
        self.conn = paramiko.SSHClient()
        self.user = username
        self.passwd = password
        if match(r"(?!255)(\d+\.){3}(?!255)\d+", host):
            self.host = host
        else:
            try:
                self.host = gethostbyname(host)
            except socket.herror:
                print "Failed to Get IP Address Of Host\n"
            except socket.error:
                print "Failed to Get IP Address of Host\n"
            except socket.timeout:
                print "Socket Timeout Error\n"
        self.conn.load_system_host_keys(filename=path.expanduser('~/.ssh/known_hosts'))
        # If not in `/.ssh/known_hosts`, then add it, and proceed.
        self.conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        RSAPrivate = '/etc/ssh/ssh_host_rsa_key'
        '''
        if os.access(RSAPrivate, os.R_OK):
            self.private_key = paramiko.rsakey.RSAKey.from_private_key_file(RSAPrivate)
        else:
            print "Do Not Have Read Access to: %s" % RSAPrivate
        '''

    def exec_command(self, cmd):
        try:
            self.conn.connect(self.host, port=22, username=self.user, password=self.passwd, timeout=20) # pkey=self.private_key)
        except paramiko.BadHostKeyException:
            print "Server host key could not be verified\n"
        except paramiko.AuthenticationException:
            print "Authentication Failed! Attempting to Connect without AD Credentials\n"
            # attempt non Active Directory Login
            new_pass = 'rootpass'
            try:
                self.conn.connect(self.host, port=22, username='root', password=new_pass, timeout=20)
            except paramiko.AuthenticationException:
                print "Standard Root Credentials Failed."
                pass
        except paramiko.ssh_exception.NoValidConnectionsError:
            print "Unable To Connect on Port 22!  Host is Likely Down Or Routing Is Wrong\n"
        except paramiko.SSHException:
            print "Error Unknown!  Failed to Establish SSH Connection!\n"

        # query = commands.getstatusoutput(cmd) - if you enable uncomment 'commands' import
        (stdin, stdout, stderr) = self.conn.exec_command(cmd)
        for line in stdout.readlines():
            print line
        self.conn.close()

def quick_role_check():
    passwd = getpass()
    csv_doc = 'splunk_forwarder_proj.csv'
    with open(csv_doc, 'rb') as dreader:
        host_reader = reader(dreader, dialect='excel', delimiter=',')
        first = True
        for row in host_reader:
            if first:
                first = False
                continue
            else:
                ipaddr = sub(r'eth0=',"",row[5])
                print "Checking Host:  %s (%s)" % (gethostbyaddr(ipaddr)[0], ipaddr)
                try:
                    check_role = SSH(passwd, ipaddr)
                    check_role.exec_command('egrep \'splunk\' /path/to/chefconfig')
                except:
                    print "Unable to Retrieve Chef Role"
                    continue
        dreader.close()

if __name__ == "__main__":
    quick_role_check()
