import urllib
import urllib2
import json
import logging

rest_logger = logging.getLogger('rest_client')

def rest_get(url,parameters,headers):
    query = urllib.urlencode(parameters)
    full_url = url + '?' + query
    rest_logger.debug( "Getting data from: {}".format(full_url) )

    req = urllib2.Request(full_url, None, headers)
    response = urllib2.urlopen(req)
    data = response.read()
    return json.loads(data)

class Rest_3Dcart:
    """A class to interact with the 3dcart REST API"""
    rest_base = 'https://apirest.3dcart.com/3dCartWebAPI/v1/'

    def __init__(self, site_url, site_token,private_key):
        self.headers = {
        'Content-Type': 'application/json;charset=UTF-8',
        'Accept': 'application/json',
        'SecureUrl': site_url,
        'PrivateKey': private_key,
        'Token':     site_token
        }

    def get_order_by_invoice_number(self,invoice_number):
        url = self.rest_base + 'Orders'
        parameters = {'invoicenumber': invoice_number}
        return rest_get(url,parameters,self.headers)
