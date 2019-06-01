import urllib.request
import json
import base64
import nacl.encoding
import nacl.signing
from storekey import return_private_key
def ping (username,password):
    """Calls the API ping and returns the response as a dictionary"""

    url = "http://cs302.kiwi.land/api/ping"
    credentials = ('%s:%s' % (username, password))
    b64_credentials = base64.b64encode(credentials.encode('ascii'))
    headers = {
        'Authorization': 'Basic %s' % b64_credentials.decode('ascii'),
        'Content-Type' : 'application/json; charset=utf-8',
    }
    
    # reads the stored key and uses that
    private_key_hex_bytes = return_private_key()



    # Uses the stored signing key hex bytes to reconstruct the key pair. 
    signing_key = nacl.signing.SigningKey(private_key_hex_bytes, encoder=nacl.encoding.HexEncoder)
    # Getting the public key 
    verify_key = signing_key.verify_key
    # Convert to bytes, then decode to string
    verify_key_hex_str =  verify_key.encode(nacl.encoding.HexEncoder).decode('utf-8')
    # For ping the message is the public key string in bytes
    message_bytes = bytes(verify_key_hex_str, encoding='utf-8')
    # Sign the message, which is the public key
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

    response_dict = json.loads(data.decode(encoding))
    return response_dict

# test if ping works
print(ping("mche226","MingChen91_1636027"))