#! /usr/bin/env python3
import socket, sys, re, os
from fileSock import framedSend, framedReceive

sys.path.append("../../lib")
import params
os.chdir("Server")

switchesVarDefaults = (
    (('l', '--listenPort'), 'listenPort', 50001),
    (('-?', '--usage'),"usage", False), #bool set if present
    (('-d', '--debug'),"debug", False),
)

progname = "echoserver"
paramMap = params.parseParams(switchesVarDefaults)

debug, listenPort = paramMap['debug'], paramMap['listenPort']
#listenAddr = ''

if paramMap['usage']:
    params.usage()

listenerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
bindAddr = ("127.0.0.1", listenPort)
listenerSocket.bind(bindAddr)
listenerSocket.listen(5)
while True:
    print("listening on: ", bindAddr)

    sock, addr = listenerSocket.accept()

    rc = os.fork() #child to handle connections
    if rc == 0:
        print("Connection recieved from ", addr)

        start = framedReceive(sock, debug)
        try:
            start = start.decode()
        except AttributeError:
            print("error exiting: ", start)
            sys.exit(0)

        count = 0
        for char in start:
            if char.isalpha():
                break
            else:
                count = count + 1
        start = start[count:]

        #where the file name ends
        start = start.split("\'start\'")

        #opening file
        file = open(start[0].strip(), "wb+")

        #recieving input while file has not ended
        while True:
            #error handling
            try:
                payload = framedReceive(sock, debug)

            except:
                pass

            if debug: print("received: ", payload)
            if not payload:
                break
            if b"\'end\'" in payload:
                file.close()
                sys.exit(0)
            else:
                file.write(payload[1:])

        #ensures child exits loop
        break
