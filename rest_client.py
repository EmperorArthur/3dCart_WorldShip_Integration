import urllib
import urllib2
import json
from pprint import pprint

PRIVATE_KEY = ''

def rest_get(url,parameters,headers):
    query = urllib.urlencode(parameters)
    full_url = url + '?' + query

    req = urllib2.Request(full_url, None, headers)
    response = urllib2.urlopen(req)
    data = response.read()
    return json.loads(data)

def get_order_by_invoice_number(invoice_number,site_url,site_token):
    rest_base = 'https://apirest.3dcart.com/3dCartWebAPI/v1/'
    url = rest_base + 'Orders'
    headers = {
        'Content-Type': 'application/json;charset=UTF-8',
        'Accept': 'application/json',
        'SecureUrl': site_url,
        'PrivateKey': PRIVATE_KEY,
        'Token':     site_token
        }
    parameters = {'invoicenumber': invoice_number}
    return rest_get(url,parameters,headers)

