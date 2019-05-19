import socket
import struct
import textwrap
import ipaddress
from datetime import datetime

IP_address = '172.16.4.192'	#Server's IP Address
Port = 10101	#Server's Port number

#Get IP Address of the machine
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


#Check if an IP Address is from a private network
def is_private(ip):
    f = struct.unpack('!I', socket.inet_pton(socket.AF_INET, ip))[0]
    private = (
        [3232235520, 4294901760],  # 192.168.0.0
        [2886729728, 4293918720],  # 172.16-31.0.0
    )
    for net in private:
        if (f & net[1]) == net[0]:
            return True
    return False


def send_lan_feedback(src, dst, t):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((IP_address, Port))
    message = 'User at {} sent file by lan transfer to {}\n Time is {}\n\n'.format(
        src, dst, t.strftime('%Y-%m-%d %H:%M:%S'))
    # sock.send('1'.encode('utf-8'))
    sock.send(message.encode('utf-8'))
    with open('log.txt', 'a') as f:
        f.write(message)
    sock.close()


def send_internet_feedback(ip, t):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((IP_address, Port))
    message = 'User at {} accessed internet.\nTime is {}\n'.format(
        get_ip(), t.strftime('%Y-%m-%d %H:%M:%S'))
    # sock.send('1'.encode('utf-8'))
    sock.send(message.encode('utf-8'))
    message += 'The sites used are:\n'
    for x in ip:
        message += x + ': ' + 'Accessed ' + str(ip[x]) + ' times\n'

    message += "\n\n"
    with open('log.txt', 'a') as f:
        f.write(message)
    sock.close()


def ethernet_frame(data):
    dest, src, proto = struct.unpack('! 6s 6s H', data[:14])
    return get_mac_address(dest), get_mac_address(src), socket.htons(proto), data[14:]


def get_mac_address(bytes_addr):
    bytes_str_map = map('{:02x}'.format, bytes_addr)
    bytes_str = list(bytes_str_map)
    ans = ''
    for i in range(len(bytes_str)):
        ans += bytes_str[i]
        if i != len(bytes_str)-1:
            ans += ':'
    return ans.upper()


def ipv4_packet(data):
    version_length = data[0]
    version = version_length >> 4
    header_length = (version_length & 15)*4
    ttl, protocol, src, dst = struct.unpack('! 8x B B 2x 4s 4s', data[:20])
    return version, header_length, ttl, protocol, ipv4(src), ipv4(dst), data[header_length:]


def ipv4(addr):
    return '.'.join(map(str, addr))


def icmp_packet(data):
    icmp_type, code, checksum = struct.unpack('! B B H', data[:4])
    return icmp_type, code, checksum, data[4:]


def tcp_segment(data):
    src, dst, seq, ack, flags = struct.unpack('! H H L L H', data[:14])
    offset = (flags >> 12)*4
    return src, dst, data[offset:]


def udp_segment(data):
    src, dst, size = struct.unpack('! H H 2x H', data[:8])
    return src, dst, size, data[8:]


conn = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(3))
with open('ip.txt') as f:
    remove = f.readlines()
    remove = [x.strip() for x in remove]

ip = dict()
total_ip_count = 0
lan_count = 0
int_last = datetime.now()
int_first = datetime.now()
lan_last = datetime.now()
lan_src = lan_dst = '127.0.0.1'
while True:
    if (datetime.now() - lan_last).total_seconds() > 2 and lan_count > 2:
        lan_count = 0
        send_lan_feedback(lan_src, lan_dst, lan_last)
    if ((datetime.now() - int_last).total_seconds() > 1 and total_ip_count > 5) or ((datetime.now() - int_first).total_seconds() > 10 and total_ip_count > 10):
        send_internet_feedback(ip, int_first)
        ip = dict()
        total_ip_count = 0
    data, addr = conn.recvfrom(65536)
    dest, src, protocol, data = ethernet_frame(data)

    # ipv4 data packets
    if protocol == 8:
        (version, header_length, ttl, protocol, src, dst, data) = ipv4_packet(data)

        # tcp protocol
        if protocol == 6:
            src_port, dst_port, data = tcp_segment(data)
            flag = 0
            for x in remove:
                if ipaddress.ip_address(dst) in ipaddress.ip_network(x):
                    flag = 1  # Contains useless internet packet
                    break

            # tcp packet from internet
            if (dst_port == 443 or dst_port == 80) and flag == 0 and len(data) > 0:
                if len(ip) == 0:
                    int_first = datetime.now()
                if dst in ip:
                    ip[dst] += 1
                else:
                    ip[dst] = 1
                total_ip_count += 1
                int_last = datetime.now()
                print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                print('Internet:')
                print('Length = {}'.format(len(data)))
                print('Source = {}, Destination = {}'.format(src, dst))
                print('\tSource Port = {}, Destination Port = {}\n\n'.format(
                    src_port, dst_port))

            # tcp packet from internal network (LAN)
            if is_private(src) and is_private(dst):
                if src != IP_address and dst != IP_address:
                    lan_count += 1
                    lan_last = datetime.now()
                    if lan_count == 1:
                        lan_src = src
                        lan_dst = dst
                    print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    print('Internal Network (LAN):')
                    print('Length = {}'.format(len(data)))
                    print('Source = {}, Destination = {}'.format(src, dst))
                    print('\tSource Port = {}, Destination Port = {}\n\n'.format(
                        src_port, dst_port))
