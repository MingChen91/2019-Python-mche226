import urllib.request
import json
import base64
import nacl.encoding
import nacl.signing
import storekey
from time import time
from get_loginserver_record import get_loginserver_record

def private_message (username,password):
    """ Use this API to transmit a secret message between users. 
    'Meta' information is public, the message itself is private """

    url = "http://210.54.33.182:80"
    credentials = ('%s:%s' % (username, password))
    b64_credentials = base64.b64encode(credentials.encode('ascii'))
    headers = {
        'Authorization': 'Basic %s' % b64_credentials.decode('ascii'),
        'Content-Type' : 'application/json; charset=utf-8',
    }
    
    #signing key 
    private_key_hex_bytes = storekey.return_private_key()
    signing_key = nacl.signing.SigningKey(private_key_hex_bytes,nacl.encoding.HexEncoder)
    

    login_server_record = get_loginserver_record(username,password)
    # targer pubkey
    target_pubkey = '11c8c33b6052ad73a7a29e832e97e31f416dedb7c6731a6f456f83a344488ec0'
    target_username = 'admin'

    message = "hello"
    message_b = bytes(message,encoding = 'utf-8')
    verifykey = nacl.signing.VerifyKey(target_pubkey, encoder = nacl.encoding.HexEncoder)
    publickey = verifykey.to_curve25519_public_key()
    sealed_box = nacl.public.SealedBox(publickey)
    encrypted = sealed_box.encrypt(message_b, encoder = nacl.encoding.HexEncoder)


    sender_created_at = str(time())

    signature_bytes = bytes(login_server_record+target_pubkey+target_username+ encrypted.decode('utf-8') +sender_created_at,encoding = 'utf-8')
    signature = signing_key.sign(signature_bytes,encoder=nacl.encoding.HexEncoder)
    payload = {
        "loginserver_record":login_server_record,
        "target_pubkey" : target_pubkey,
        "target_username" : target_username,
        "encrypted_message":encrypted.decode('utf-8'),
        "sender_created_at": sender_created_at,
        "signature": signature.signature.decode('utf-8')

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

    # response_dict = json.loads(data.decode(encoding))
    # return response_dict

# test if ping works
print(private_message("mche226","MingChen91_1636027"))