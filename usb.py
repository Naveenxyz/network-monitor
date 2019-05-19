import socket
from datetime import datetime
import sys
global a
with open('/home/naveen/np/usb.log', 'r') as f:
    global a
    a = f.read()
    if a == "":
        print("nothing present")
        sys.exit()
    print(type(a))
    f.close()
open("usb.log", "w").close()
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
IP_address = '172.16.4.192'
Port = 10101
server.connect((IP_address, Port))
server.send(a.encode('utf-8'))
