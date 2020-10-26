#! /usr/bin/env python3

#Author: Jose Gallardo


import socket, sys, re, os
from encapFramedSock import EncapFramedSock
sys.path.append("../../lib") #for params
import params

port = input("Would you like to use the stammer proxy? (y/n)\n")
if 'y' in port:
    port = "50000"
else:
    port = "50001"

switchesVarDefaults = (
    (('-s', '--server'), 'server', "127.0.0.1:" + port),
    (('-?', '--usage'), "usage", False), # bool set if present
    (('-d', '--debug'), "debug", False),
)

progname = "fileClient"
paramMap = params.parseParams(switchesVarDefaults)

server, usage, debug = paramMap["server"], paramMap["usage"], paramMap["debug"]

if usage:
    params.usage()

try:
    serverHost, serverPort = re.split(":", server)
    serverPort = int(serverPort)
except:
    print("Cant parse server:port from '%s'" % server)
    sys.exit(1)

s = None
sa = None
fsock = None
for res in socket.getaddrinfo(serverHost, serverPort, socket.AF_UNSPEC, socket.SOCK_STREAM):
    af, socketType, proto, cannonname, sa = res
    try:
        print("Creating Socket: af=%d, type=%d, proto=%d" % (af, socketType, proto))
        s = socket.socket(af, socketType, proto)
    except socket.error as msg:
        print(" error: %s" % msg)
        s = None
        continue
    try:
        print("Attempting to connect to %s" % repr(sa))
        s.connect(sa)
        fsock = EncapFramedSock((s, sa))
    except socket.error as msg:
        print("Error: %s" % msg)
        s.close()
        s = None
        continue
    break

if s is None:
    print("Could not open socket")
    sys.exit(1)

files = os.listdir(os.curdir)
print(files)
inputFile = input("Please select a file to send \n")
#Attempt to read input as file
try:
    with open(inputFile.strip(), "rb") as binaryFile:
        #read whole file as one
        data = binaryFile.read()
        if data == b'':
            print(inputFile + " is empty....Now Exiting")
            sys.exit(0)
except FileNotFoundError:
    print("File not found....Now Exiting")
    sys.exit(0)
try:
    #sends file info to server
    fsock.send(b':'+inputFile.strip().encode('utf-8') + b"\'start\'")
except BrokenPipeError:
    print("Disconnected from server")
    sys.exit(0)

while len(data) >= 100:
    line = data[:100]
    data = data[100:]
    try:
        fsock.send(b":"+line,debug)
    except BrokenPipeError:
        print("Disconected from server")
        sys.exit(0)

if len(data) > 0:
    fsock.send(b":"+data,debug)

try:
    fsock.send(b":\'end\'")
except BrokenPipeError:
    print("Disconnected form server")
    sys.exit(0)