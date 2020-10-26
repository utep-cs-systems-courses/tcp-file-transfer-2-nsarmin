#! /usr/bin/env python3

#Author: Jose Gallardo

import socket, sys, re, os, threading
from threading import Thread, Lock
from encapFramedSock import EncapFramedSock

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
print("listening on: ", bindAddr)
lock = threading.Lock()

class Server(Thread):
    def __init__(self, sockAddr):
        Thread.__init__(self)
        self.sock, self.addr = sockAddr
        self.fsock = EncapFramedSock(sockAddr)

    def run(self):
        print("New thread handling connection from ", self.addr)
        while True:
            lock.acquire()
            start = self.fsock.receive(debug)
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
                    payload = self.fsock.receive(debug)

                except:
                    pass

                if debug: print("received: ", payload)
                if not payload:
                    break
                if b"\'end\'" in payload:
                    file.close()
                    lock.release()
                    sys.exit(0)
                else:
                    file.write(payload[1:])


while True:
    sockAddr = listenerSocket.accept()
    server = Server(sockAddr)
    server.start()
