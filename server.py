import socket
import select
from thread import *
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


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

IP_address = get_ip()
Port = 10101
server.bind((IP_address, Port))


server.listen(100)
list_of_clients = []


def clientthread(conn, addr):
    while True:
        try:
            message = conn.recv(65536)
            if message:
                print("<" + addr[0] + "> " + message)
            else:
                remove(conn)

        except:
            continue


def remove(connection):
    if connection in list_of_clients:
        list_of_clients.remove(connection)


while True:

    conn, addr = server.accept()
    list_of_clients.append(conn)
    start_new_thread(clientthread, (conn, addr))

conn.close()
server.close()
