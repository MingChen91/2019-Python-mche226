import urllib.request
import json
import base64
import nacl.encoding
import nacl.signing
from storekey import return_private_key

def ping (username,password):
    """Calls the API ping and returns the response as a dictionary"""

    url = "http://cs302.kiwi.land/api/ping"
    
    # reads the stored key and uses that
    private_key_hex = return_private_key()

    #create HTTP BASIC authorization header
    # username = "Mche226"
    # password = "MingChen91_16360"

    credentials = ('%s:%s' % (username, password))
    b64_credentials = base64.b64encode(credentials.encode('ascii'))
    headers = {
        'Authorization': 'Basic %s' % b64_credentials.decode('ascii'),
        'Content-Type' : 'application/json; charset=utf-8',
    }


    # Generate a new random signing key / private key generation and converting to json format
    signing_key = nacl.signing.SigningKey(private_key_hex, encoder=nacl.encoding.HexEncoder)

    #public pair / converting to json
    verify_key = signing_key.verify_key
    verify_key_hex_str =  verify_key.encode(nacl.encoding.HexEncoder).decode('utf-8')

    message_bytes = bytes(verify_key_hex_str, encoding='utf-8')
    #sign the message, which is the public + name
    signed = signing_key.sign(message_bytes, encoder=nacl.encoding.HexEncoder)
    signature_hex_str = signed.signature.decode('utf-8')


    payload = {
        "pubkey" : verify_key_hex_str,
        "signature" : signature_hex_str,
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

    response = json.loads(data.decode(encoding))
    return response 

print(ping("Mche226","MingChen91_1636027"))