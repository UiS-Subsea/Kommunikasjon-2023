import socket
import struct


class CAN:
    def __init__(self, name:str, filter_id:hex, filter_mask:hex):
        self.name = name
        self.filter_id = filter_id      #= 0x123
        self.filter_mask = filter_mask  #= 0x7FF
        self.can_socket = socket.socket(socket.AF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
        self.can_socket.bind((self.name,))
        self.filter_flags = socket.CAN_EFF_FLAG
        self.filter_struct = struct.pack("=IB3x", self.filter_id, self.filter_flags)
        self.can_socket.setsockopt(socket.SOL_CAN_RAW, socket.CAN_RAW_FILTER, self.filter_struct)

    def recive(self):
        msg = self.can_socket.recv(16)
        can_id, length, data = struct.unpack('<IB3x8s', msg)
        return can_id, data
    
    def send(self, can_id, data):
        can_pkt = struct.pack("<LB3x8s", can_id, len(data), data)
        self.can_socket.send(can_pkt)
