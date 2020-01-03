import threading
import socket
import select
import sys

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        local_ip = s.getsockname()[0]
    except:
        local_ip = '127.0.0.1'
    finally:
        s.close()
    return local_ip

def clientthread(conn, addr):
    while True:
        try:
            message = conn.recv(65536)
            if message:
                print("<" + addr[0] + "> " + message.decode('utf-8'))
                conn.send("hello".encode('utf-8'))
                message2=conn.recv(65536)
                print(message2.decode('utf-8'))
                conn.send("got something new".encode('utf-8'))
            else:
                retur
        except:
            continue

threads = list()
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
IP_address = get_ip()
Port = 10101
server.bind((IP_address, Port))
server.listen(100)

while True:
    conn, addr = server.accept()
    x = threading.Thread(target=clientthread, args=(conn,addr))
    threads.append(x)
    x.start()

conn.close()
server.close()
