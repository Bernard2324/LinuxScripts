#!/usr/bin/env python

import time
import getpass
import subprocess
from netmiko import ConnectHandler

class connectNet(object):
	def __init__(self, typd, addr, user, passwd, secret='secret'):
		self.hostObj = {
			'device_type': typd,
			'ip': addr,
			'username': user,
			'password': passwd,
			'secret': secret
		}
		print "[*] Connecting to %s\n" % addr
		self.connection = ConnectHandler(**self.hostObj)

	def escalate(self):
		if not self.connection.check_enable_mode():
			try:
				self.connection.enable()
			except:
				print "Failed to Enter enable Mode!\n"
		else:
			pass

	def getConfigure(self):
		# enter enable mode
		if not self.connection.check_config_mode():
			try:
				self.connection.config_mode()
			except:
				print "Failed To Enter Configuration Terminal Mode!\n"
		else:
			print "Entered Config Mode"

	def commands(self, command_set):
		start = time.time()
		results = self.connection.send_config_set(command_set)
		end = time.time()
		elapsed = (end-start)
		print "\t[*] [Elapsed Time]: %s seconds" % elapsed

	def end(self):
		self.connection.cleanup()
		print "[*] Connection Closed"


def descriptions():

	patch_panel = {
		1: "1",
		2: "49",
		3: "97",
		4: "145"
	}
	all_interfaces = {}

	for stack in range(1, 5):
		init_val = int(patch_panel.get(stack))
		for port in range(1, 49):
			Interface = "GigabitEthernet%s/0/%s" % (stack, port)
			all_interfaces[Interface] = "11.D.0%s" % (init_val)
			init_val += 1
	# now we have a list of all interfaces
	# and their corresponding patch panel number.  We can now develop a command for automation
	print "Please Enter Your Password!"
	quickpass = getpass.getpass()
	net_conn = connectNet('device type here', '1.1.1.1', 'johndoe123', quickpass)

	for interface, patch in all_interfaces.iteritems():
		int_desc = "description Patch: %s" % patch
		int_command = "interface %s" % interface
		config_set = [int_command, int_desc]
		# net_conn.configure()
		print "Config Buffer: %s" % config_set
		net_conn.escalate()
		net_conn.getConfigure()
		try:
			net_conn.commands(config_set)
		except:
			print "Failed"
		# close the connection
	net_conn.end()

if __name__ == "__main__":
	subprocess.call('clear', shell=True)
	descriptions()