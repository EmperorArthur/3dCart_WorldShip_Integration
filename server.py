#!/usr/bin/python

import SocketServer
import modules.psql_server as psql_server
from modules.rest_client import Rest_3Dcart
import logging
from pprint import pprint

logging.basicConfig(level=logging.INFO)

class psql_3dCart(psql_server.psql_server):
    api = Rest_3Dcart('','','')

    def handle_query(self,query):
        """
        Handle SQL Querys
        Specifically designed to give order informfation to this query:
        'select * from orders where InvoiceNumber=<invoice_number>;'
        """
        invoice_number = None
        response = None

        query = query.lower().strip(';')
        words = query.split(' ')

        query_type    = words[0]
        if 'from' in words:
            from_position = words.index('from')
        else:
            from_position = -1
        if 'where' in words:
            where_position = words.index('where')
        else:
            where_position = -1

        if(query_type == "select" and where_position != -1):
            where_clauses = words[where_position+1:]
            for clause in where_clauses:
                where_pair = clause.split('=')
                if('invoicenumber' == where_pair[0]):
                    invoice_number = where_pair[1]
            if(invoice_number != None):
                logging.info("Getting order information for invoice number: {}".format(invoice_number))
                response = self.api.get_order_by_invoice_number(invoice_number)
                self.select_response(response)
        #Default if command does not fit specified syntax
        self.send_data(psql_server.CommandComplete(query_type+" 0"))
        self.send_data(psql_server.ReadyForQuery)

server = SocketServer.TCPServer(("0.0.0.0", 5432), psql_3dCart)
try:
    server.serve_forever()
except:
    server.shutdown()
