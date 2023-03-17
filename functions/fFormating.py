#!/usr/bin/python3

"""
    @file   packetBuild.py
    
    @brief  
    @date   16.03.23 
    @author Thomas Matre
"""
import can
import struct

can_types = {
    "int8": "<b",
    "uint8": "<B",
    "int16": "<h",
    "uint16": "<H",
    "int32": "<i",
    "uint32": "<I",
    "int64": "<q",
    "uint64": "<Q",
    "float": "<f"
}


def getByte(can_format:str, number):
    return list(struct.pack(can_types[can_format], number))

def getNum(can_format:str, byt):
    if isinstance(byt, int):
        byt = byt.to_bytes(1, byteorder="big")
    return struct.unpack(can_types[can_format], byt)[0]

def getBit(num, bit_nr):
    return (num >> bit_nr) & 1

def setBit(bits: tuple):
    return sum(bit << k for k, bit in enumerate(bits))
#formats to json format in agreed upon formating
def toJson(input):
    packet_sep = json.dumps("*")
    return bytes(packet_sep + json.dumps(input) + packet_sep, "utf-8")