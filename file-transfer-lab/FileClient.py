#! /usr/bin/env python3

# Echo client program
import socket, sys, re

from os.path import exists

sys.path.append("../lib")       # for params
import params

from framedSock import framedSend, framedReceive



switchesVarDefaults = (
    (('-s', '--server'), 'server', "127.0.0.1:50001"),
    (('-d', '--debug'), "debug", False), # boolean (set if present)
    (('-?', '--usage'), "usage", False), # boolean (set if present)
)


progname = "framedClient"
paramMap = params.parseParams(switchesVarDefaults)

server, usage, debug  = paramMap["server"], paramMap["usage"], paramMap["debug"]
