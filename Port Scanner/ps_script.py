import socket
import os
import struct
import threading
from ipaddress import ip_address, ip_network
from ctypes import *

LISTEN_ADDR = "192.168.0.187"
TARGET_NETWORK = "192.168.0.0/24"
MAGIC_PAYLOAD = "HA!"
UDP_PORT = 65212

def send_udp_probes(network, payload):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    for ip in ip_network(network).hosts():
        sock.sendto(payload.encode('utf-8'), (str(ip), UDP_PORT))

class IPHeader(Structure):
    _fields_ = [
        ("ihl", c_ubyte, 4),
        ("version", c_ubyte, 4),
        ("tos", c_ubyte),
        ("len", c_ushort),
        ("id", c_ushort),
        ("offset", c_ushort),
        ("ttl", c_ubyte),
        ("protocol_num", c_ubyte),
        ("sum", c_ushort),
        ("src", c_uint32),
        ("dst", c_uint32)
    ]
    def __new__(cls, socket_buffer=None):
        return cls.from_buffer_copy(socket_buffer)
    def __init__(self, socket_buffer=None):
        self.socket_buffer = socket_buffer
        self.protocol_map = {1: "ICMP", 6: "TCP", 17: "UDP"}
        self.src_address = socket.inet_ntoa(struct.pack("@I", self.src))
        self.dst_address = socket.inet_ntoa(struct.pack("@I", self.dst))
        try:
            self.protocol = self.protocol_map[self.protocol_num]
        except:
            self.protocol = str(self.protocol_num)

class ICMPHeader(Structure):
    _fields_ = [
        ("type", c_ubyte),
        ("code", c_ubyte),
        ("checksum", c_ushort),
        ("unused", c_ushort),
        ("next_hop_mtu", c_ushort)
    ]
    def __new__(cls, socket_buffer):
        return cls.from_buffer_copy(socket_buffer)
    def __init__(self, socket_buffer):
        self.socket_buffer = socket_buffer

if os.name == "nt":
    proto = socket.IPPROTO_IP
else:
    proto = socket.IPPROTO_ICMP

sniff_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, proto)
sniff_socket.bind((LISTEN_ADDR, 0))
sniff_socket.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

if os.name == "nt":
    sniff_socket.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

sender_thread = threading.Thread(target=send_udp_probes, args=(TARGET_NETWORK, MAGIC_PAYLOAD))
sender_thread.start()

try:
    while True:
        packet = sniff_socket.recvfrom(65535)[0]
        ip_hdr = IPHeader(packet[:20])
        print("Protocol: %s %s -> %s" % (ip_hdr.protocol, ip_hdr.src_address, ip_hdr.dst_address))
        if ip_hdr.protocol == "ICMP":
            offset = ip_hdr.ihl * 4
            buf = packet[offset:offset + sizeof(ICMPHeader)]
            icmp_hdr = ICMPHeader(buf)
            print("ICMP -> Type: %d Code: %d" % (icmp_hdr.type, icmp_hdr.code))
            if icmp_hdr.code == 3 and icmp_hdr.type == 3:
                if ip_address(ip_hdr.src_address) in ip_network(TARGET_NETWORK):
                    if packet[-len(MAGIC_PAYLOAD):] == MAGIC_PAYLOAD.encode('utf-8'):
                        print("Host Up: %s" % ip_hdr.src_address)
except KeyboardInterrupt:
    if os.name == "nt":
        sniff_socket.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)