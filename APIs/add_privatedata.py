import urllib.request
import json
import base64
import nacl.encoding
import nacl.signing
import storekey
from time import time
from get_loginserver_record import get_loginserver_record

def add_privatedata (username,password,private_data):
    """Use this API to save symmetrically encrypted private data for a given user. It will
        automatically delete previously uploaded private data.
        
        TODO
        --NEED TO IMPLEMENT ENCRYPTION FOR PRIVATE DATA--
        """

    url = "http://cs302.kiwi.land/api/add_privatedata"

    credentials = ('%s:%s' % (username, password))
    b64_credentials = base64.b64encode(credentials.encode('ascii'))
    headers = {
        'Authorization': 'Basic %s' % b64_credentials.decode('ascii'),
        'Content-Type' : 'application/json; charset=utf-8',
    }
    
    # reads the stored key and uses that
    private_key_hex_bytes = storekey.return_private_key()


    # Uses the stored signing key hex bytes to reconstruct the key pair. 
    signing_key = nacl.signing.SigningKey(private_key_hex_bytes, encoder=nacl.encoding.HexEncoder)
        
    loginserver_record_str = get_loginserver_record(username,password)
    
    client_saved_at = str(time())

    signature_bytes = bytes( private_data + loginserver_record_str + client_saved_at,encoding='utf-8')
    signature = signing_key.sign(signature_bytes,encoder=nacl.encoding.HexEncoder)
    signature_hex_str = signature.signature.decode('utf-8')

    payload = {
        "privatedata" : private_data,
        "loginserver_record" : loginserver_record_str,
        "client_saved_at" : client_saved_at,
        "signature" : signature_hex_str
    }
    
    payload_str = json.dumps(payload)
    payload_data = payload_str.encode('utf-8')

    try:
        # report
        req = urllib.request.Request(url, data=payload_data, headers=headers)
        response = urllib.request.urlopen(req)
        data = response.read() # read the received bytes
        encoding = response.info().get_content_charset('utf-8') #load encoding if possible (default to utf-8)
        response.close()
        
    except urllib.error.HTTPError as error:
        print(error.read())
        exit()

    response_dict = json.loads(data.decode(encoding))
    return response_dict

# test if ping works
print(add_privatedata("mche226","MingChen91_1636027","attack at dawn"))