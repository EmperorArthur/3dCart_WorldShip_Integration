#!/bin/python

"""
A basic python implementation of a Postgresql server

Subclass psql_server, and re-define handle_query

To test, use `psql -h <server_ip> -p 5432` and enter any password at the prompt.
By default, "select;" returns a basic response table, but everything else just responds with a succeeded message.
"""

import SocketServer
import socket
import struct
import logging

server_logger = logging.getLogger('psql_server')

###############################################################
# Data structs, checkers, and parsers
# See https://www.postgresql.org/docs/8.1/static/protocol-message-formats.html
AuthenticationOK                = struct.pack("!cii", 'R', 8, 0)
AuthenticationCleartextPassword = struct.pack("!cii", 'R', 8, 3)
ReadyForQuery                   = struct.pack("!cic", 'Z', 5, 'I')


def CommandComplete(command_tag):
    #End '\x00' + 4 byte length = 5
    return struct.pack("!ci", 'C', len(command_tag)+5)+command_tag+'\x00'

#A field identifier for a single text field.  For use with RowDescription_text
def Text_field(field_name):
    tableid = 0         #defaults to 0
    columnid = 0        #defaults to 0
    datatypeid = 0      #Just putting a number here, should find out what represents 'text' at some point
    datatypesize = -1   #Negatives mean variable size
    typemodifier = -1   #This is based on datatypeid, and I have no idea what I'm doing
    format_code = 0     #0 for text, and 1 for binary
    return field_name + '\x00' + struct.pack("!ihihih", tableid, columnid, datatypeid, datatypesize, typemodifier, format_code)

#Cheat and say all fields are of type 'text'
def RowDescription_text(field_names):
    fields = ""
    for i in field_names:
        fields += Text_field(i)
    # Ignore 'C', 4 + 2 + length of all field information
    return struct.pack("!cih", 'T', 6+len(fields), len(field_names)) + fields

#Cheat and convert everything sent into strings/text
def DataRow_text(row):
    data = ""
    for i in row:
        i = str(i)
        data += struct.pack("!i", len(i)) + i
    #4 bytes + 2 bytes + all data
    return struct.pack("!cih", 'D', 6+len(data), len(row)) + data

def Is_SSLRequest(data):
    try:
        msglen, sslcode = struct.unpack("!ii", data)
    except:
        return False
    if ( msglen == 8 and sslcode == 80877103):
        return True
    return False

#Returns a list of strings sent, or False if not a StartupMessage or something went wrong
def Parse_StartupMessage(data):
    if(len(data) < 8):
        server_logger.error("StartupMessage must contain at least 8 bytes!")
        return False
    msglen, protoversion = struct.unpack("!ii", data[0:8])
    if(msglen != len(data) or protoversion != 196608):
        server_logger.error("StartupMessage is corrupt!")
        if(msglen != len(data)):
            server_logger.error("Expected {} bytes.  Recieved {} bytes.".format(msglen,len(data)))
        else:
            server_logger.error("Expected protocol version 196608. Recieved {}.".format(protoversion))
        return False
    parameters_string = data[8:]
    return parameters_string.split('\x00')

#Returns a Password, or False if not a PasswordMessage or something went wrong
def Parse_PasswordMessage(data):
    if(len(data) < 5):
        server_logger.error("PasswordMessage must contain at least 5 bytes!")
        return False
    msg_type, msglen = struct.unpack("!ci", data[0:5])
    msglen += 1 #length doesn't include msg_type
    if(msg_type != 'p'):
        server_logger.error("Not a PasswordMessage!")
        return False
    if(msglen != len(data)):
        server_logger.error("PasswordMessage is corrupt!")
        server_logger.error("Expected {} bytes.  Recieved {} bytes.".format(msglen,len(data)))
        return False
    return data[5:]

#Returns a Query, or False if not a Query or something went wrong
def Parse_Query(data):
    if(len(data) < 5):
        server_logger.error("Query must contain at least 5 bytes!")
        return False
    msg_type, msglen = struct.unpack("!ci", data[0:5])
    msglen += 1 #length doesn't include msg_type
    if(msg_type != 'Q'):
        server_logger.error("Not a Query!")
        return False
    if(msglen != len(data)):
        server_logger.error("Query is corrupt!")
        server_logger.error("Expected {} bytes.  Recieved {} bytes.".format(msglen,len(data)))
        return False
    return data[5:].strip('\x00')

###############################################################

class psql_server(SocketServer.BaseRequestHandler):
    def handle(self):
        try:
            peer_name=self.request.getpeername()
            server_logger.info("Connection established from {0}:{1}".format(peer_name[0],peer_name[1]))

            #Handle SSL (Don't do SSL)
            data = self.get_data()
            if(Is_SSLRequest(data)):
                self.send_data("N")
                data = self.get_data()

            server_logger.info( "Startup Message: "+ repr(Parse_StartupMessage(data)) )

            #Handle Authentication
            self.send_data(AuthenticationCleartextPassword)
            data = self.get_data()
            if(data):
                server_logger.info("Password: {}".format(Parse_PasswordMessage(data)))
            else:
                server_logger.info("No Password recieved.  Closing Connection.")
                return
            self.send_data(AuthenticationOK)

            self.send_data(ReadyForQuery)
            server_logger.debug("Startup Completed")
            ###End Startup Code

            #As long as querys come, continue answering them
            data = self.get_data()
            while(data):
                query = Parse_Query(data);
                if(isinstance(query,str)):
                    server_logger.info( "Recieved Query: {}".format(repr(query)) )
                    self.handle_query(query);
                else:
                    return
                data = self.get_data()
        except socket.error as e:
            server_logger.info("Client closed connection.")

    def handle_query(self,query):
        query_type = query.split(' ')[0].strip(';').upper()
        if(query_type == "SELECT"):
            dicts = [{'abc':1, 'def':2},{'abc':3, 'def':4}]
            self.select_response(dicts)
        else:
            self.send_data(CommandComplete(query_type+" 0"))
            self.send_data(ReadyForQuery)

    def select_response(self,response_dicts):
        """
        Provides a response to SELECT commands.
        Expects all dicts to have the same keys
        The field names are taken from the keys of the first dict.
        Assumes dict.keys() and dict.values() returns items in the same order
        """
        keys = response_dicts[0].keys()

        self.send_data(RowDescription_text(keys))
        for row in response_dicts:
            self.send_data(DataRow_text(row.values()))

        self.send_data(CommandComplete("SELECT {}".format(len(response_dicts))))
        self.send_data(ReadyForQuery)

    def get_data(self):
        server_logger.debug("Recieving Data")
        data = self.request.recv(1024)
        #server_logger.debug("Received {} bytes: {}".format(len(data), repr(data)))
        return data

    def send_data(self,data):
        server_logger.debug("Sending {} bytes".format(len(data)))
        #server_logger.debug(repr(data))
        return self.request.sendall(data)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    #logging.basicConfig(level=logging.DEBUG)
    server = SocketServer.TCPServer(("0.0.0.0", 5432), psql_server)
    try:
        server.serve_forever()
    except:
        server.shutdown()
