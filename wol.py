import struct, socket, sys 

if len(sys.argv)>1: 
    PC = sys.argv[1].upper()
else: 
    PC = 'ZHIRAFFA'

PCs = {'ZHIRAFFA': '2C:27:D7:19:70:CF', 
       'KROT' : '00:b3:f6:03:09:85', 
       'MONSTER' : '1c:6f:65:d5:3c:b6', 
       'SNAKE': 'ac:de:48:d0:eb:98', 
       'SONY-WIN7': '00:1b:77:76:e0:47'}

def WakeOnLan(ethernet_address):

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

WakeOnLan(PCs[PC])