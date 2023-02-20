import can
import struct
import time
import json

can_types = {
    "int8": ">b",
    "uint8": ">B",
    "int16": ">h",
    "uint16": ">H",
    "int32": ">i",
    "uint32": ">I",
    "int64": ">q",
    "uint64": ">Q",
    "float": ">f"
}

def get_byte(can_format:str, number):
    return list(struct.pack(can_types[can_format], number))

def get_num(can_format:str, byt):
    if isinstance(byt, int):
        byt = byt.to_bytes(1, byteorder="big")
    return struct.unpack(can_types[can_format], byt)[0]

def get_bit(num, bit_nr):
    return (num >> bit_nr) & 1

def set_bit(bits: tuple):
    return sum(bit << k for k, bit in enumerate(bits))
#formats to json
def to_json(input):
    packet_sep = json.dumps("*")
    return bytes(packet_sep + json.dumps(input) + packet_sep, "utf-8")

#builds packs for canbus
def packetBuild(tags):
  canID, *idData = tags
  idDataByte = []
  for data in idData:
    try:
      idDataByte += struct.pack(can_types[data[0]], *data[1:])
    except struct.error as e:
      print(f"Error: {e}")
      print(f"data={data}, format={data[0]}, value={data[1:]}")
      print(f"idDataByte={idDataByte}")

  return can.Message(arbitration_id=canID, data=idDataByte, is_extended_id=False)

#decodes packs
def packetDecode(msg):
  canID = msg.arbitration_id
  dataByte = msg.data
  if canID == 10:
    pack1 = get_num("int16", dataByte[0:2])
    pack2 = get_num("int16", dataByte[2:4])
    pack3 = get_num("int16", dataByte[4:6])
    pack4 = get_num("int16", dataByte[6:8])
    json_dict = {"name10": (pack1, pack2, pack3, pack4)}
  elif canID == 52:
    pack1 = get_num("int32", dataByte[0:4])
    pack2 = get_num("int8",  dataByte[4])
    pack3 = get_num("uint8", dataByte[5])
    pack4 = get_num("uint16", dataByte[6:8])
    json_dict = {"name52": (pack1, pack2, pack3, pack4)}
  else:
    return f"Unknown CanID: {canID} recived from ROV system"
  return to_json(json_dict)


if __name__ == "__main__":
  t = time.time()
# tag = (type, value)
  tag0 = ("int32", 7600001)
  tag1 = ("int8", 120)
  tag2 = ("uint8", 240)
  tag3 = ("uint16", 50000 )
# tags = (id, tag0, tag1, tag2, tag3, tag4, tag5, tag6, tag7)
  id65tags = (65, tag0, tag1, tag2, tag3)
  print(packetBuild(id65tags))

  print(packetDecode(can.Message(timestamp=1676392071.679734, arbitration_id=0x34, is_extended_id=False, channel='can0', dlc=8, data=[0x00, 0x73, 0xf7, 0x81, 0x78, 0xF0, 0xC3, 0x50])))

  elapsed = time.time() - t
  print(f"elapsed time: {elapsed}")

  #tag0 = ("int16", 16550)
  #tag4 = ("int16", -20000)
  #print(get_byte(tag0[0],tag0[1]))
  #print(get_byte("int32", 76100001))