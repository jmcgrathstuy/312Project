import socketserver
import sys
import time
import secrets
import hashlib
import base64
import json

def handle(data):
    datatype = ''
    opcode = data[0] & 15
    payload = bytes()
    payloadstart = 0
    #print(opcode)
    #print((8).to_bytes(1, 'big'))
    if opcode == (8):
        #???close connection
        #this still needs to be written
        return(payload, 'close')
    elif opcode == 1:#(1).to_bytes(1, 'big'):
        datatype = 'text'
    elif opcode == 2:#(2).to_bytes(1, 'big'):
        datatype = 'bytes'

    #TypeError: unsupported operand type(s) for &: 'int' and 'bytes'

    length = data[1] & (127)
    
    ##???Large payload case payload >= 65536 bytes
    if(length == (127).to_bytes(1, 'big')):
        maskbytes = []
        for i in [10,11,12,13]:
            maskbytes.append(data[i])
        lenbytes = []
        for i in [2,3,4,5,6,7,8,9]:
            lenbytes.append(data[i])
        lenint = int.from_bytes(lenbytes)
        payloadstart = 14

    ##???Medium payload case payload >= 126 bytes, < 65536
    elif(length == (126).to_bytes(1, 'big')):
        maskbytes = []
        for i in [4,5,6,7]:
            maskbytes.append(data[i])
        lenbytes = []
        for i in [2,3]:
            lenbytes.append(data[i])
        lenint = int.from_bytes(lenbytes)
        payloadstart = 8

    #???small case payload < 126 bytes
    else:
        maskbytes = []
        for i in [2,3,4,5]:
            maskbytes.append(data[i])
        payloadstart = 6
        lenint =  length

    #Goes byte by byte, masking and appending to the payload
    mo = 0

    for byte in data[payloadstart:payloadstart + (lenint)]:
    #for byte in data[payloadstart:payloadstart]:
        maskbyte = maskbytes[mo%4]
        payload += (byte ^ maskbyte).to_bytes(1, 'big')
        mo = ((mo + 1) % 4)
        

    return (payload, datatype, opcode)

#Constructs a websocket frame with given data in the payload
#data is a bytearray
def buildFrame(data):
    frame = bytearray() 
    frame.append(129)
    length = len(data)
    payloadstart = 0
    if length < 126:
        frame.append(length)
        payloadstart = 2
    elif length < 65536:
        frame.append(126)
        lenbytes = length.to_bytes(2, 'big')
        frame.append(lenbytes)
        payloadstart = 4
    else: # length >= 65536
        frame.append((127).to_bytes(1, 'big'))
        lenbytes = length.to_bytes(8, 'big')
        frame.append(lenbytes)
        payloadstart = 10

    for byte in data:
        frame.append(byte)
    return frame