"simple Wake On Line > sendign magic packet to PC to wake up"
from __future__ import print_function
import struct, socket, sys

def wol(PC = ['SURFACE']):
    PCs = {#'ZHIRAFFA': '2C:27:D7:19:70:CF',
           #'KROT' : '00:b3:f6:03:09:85',
           #'MONSTER' : '1c:6f:65:d5:3c:b6',
           'SURFACE' : '58:82:A8:94:82:02',
           'HIPPO' : 'c8:60:00:cc:8e:16'}

    ethernet_address = PCs[PC[0].upper()]
  # Construct a six-byte hardware address

    addr_byte = ethernet_address.split(':')
    hw_addr = struct.pack('BBBBBB', int(addr_byte[0], 16),
    int(addr_byte[1], 16),
    int(addr_byte[2], 16),
    int(addr_byte[3], 16),
    int(addr_byte[4], 16),
    int(addr_byte[5], 16))

    # Build the Wake-On-LAN "Magic Packet"...
    msg = '\xff' * 6 + hw_addr * 16
    # ...and send it to the broadcast address using UDP
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.sendto(msg, ('<broadcast>', 9))
    s.close()
    print('sent to + ' + PC[0] + ' : ' + ethernet_address)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        wol([sys.argv[1]])
    else:
        wol()