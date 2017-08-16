#!/usr/bin/python

from modules.rest_client import Rest_3Dcart
from pprint import pprint
import logging

#logging.basicConfig(level=logging.DEBUG)

api = Rest_3Dcart('','','')
order = api.get_order_by_invoice_number(<invoice_number>)
pprint(order)
print "Got {} orders.".format(len(order))
