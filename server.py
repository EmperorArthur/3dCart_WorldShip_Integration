#!/usr/bin/python

import SocketServer
from modules.psql_server import psql_server
import logging

logging.basicConfig(level=logging.INFO)

server = SocketServer.TCPServer(("0.0.0.0", 5432), psql_server)
try:
    server.serve_forever()
except:
    server.shutdown()
