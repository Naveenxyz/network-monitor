import socket
message="this is a message"
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
IP_address = '10.0.2.156'
Port = 10101
server.connect((IP_address, Port))
server.send(message.encode('utf-8'))
reply=server.recv(65536)
print(reply.decode('utf-8'))
message2="this is the message 2"
server.send(message2.encode('utf-8'))
reply2=server.recv(65536)
print(reply2.decode('utf-8'))