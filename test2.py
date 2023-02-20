from time import sleep
import can

bus1 = can.interface.Bus(channel = 'test', bustype = 'virtual')
bus2 = can.interface.Bus('test', bustype='virtual')

msg = can.Message(arbitration_id=0x13, data=[0, 1, 2, 3, 4, 5, 6, 7])

def parseData(can):
        print( can.arbitration_id )
        print(can.data)
        print(bus2.recv())

notifier = can.Notifier(bus2,[parseData])

while (1):
    bus1.send(msg)
    print("loopdone")
    sleep(1)