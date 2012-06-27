#!/bin/sh

# written in 2.6; accepts a sleep time 'python monarp.py 5' for 5 second sleeps

import os
import re
import string
import time
import sys
import subprocess
from threading import Thread

# clean up the entry
def clean (line):
	line = string.replace(line, '(', '')
	return string.replace(line, ')', '')

# make sure our connection is solid still
def check_connection():
	while running:
		addr = "192.168.1.118"
		process = subprocess.Popen(['ping', '-c', '1', '-W', '2', addr], 
					               stdout=subprocess.PIPE, 
					               stderr=subprocess.PIPE)
		process.wait()
		line = process.stdout.read().decode('utf-8')
		if re.search("\d received", line).group(0) != "1 received":
			print "[-] Network is down!"
		time.sleep(3)

entries = {}
running = True

# first parameter is the sleep length; default of 5s
if len(sys.argv) > 1:
	sleep = int(sys.argv[1])
else:
	sleep = 5

try:
	# start connection thread
	thread = Thread(target=check_connection)
	thread.start()
	print "[+] Starting monarp..."
	while True:
		# gather the ARP cache
		lines = os.popen('/usr/sbin/arp -a')
		for i in lines:
			# parse the cache
			ip = re.search ( '\(.*\)', i )
			mac = re.search( 'at (.*? )', i).group(1)
			ip = clean ( ip.group(0) )

			print "%s\t%s"%(ip, mac)
			if ip in entries:
				if not entries[ip] == mac:
					print "MAC has changed for IP %s (%s-> %s)"%(ip, entries[ip], mac)
					entries[ip] = mac
			else:
				entries[ip] = mac
			
		time.sleep(sleep)
except KeyboardInterrupt:
	running = False	
