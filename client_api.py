import urllib.request
import json
import nacl.encoding
import nacl.signing
from time import time
import key_manager
import server_api
import helper_modules

def broadcast(username,message = "Default Message"):
    """ Use this api to transmit a signed broadcast between users. """

    # url = "http://cs302.kiwi.land/api/rx_broadcast"
    url = "http://172.23.114.169:1234/api/rx_broadcast"
    api_key = key_manager.return_apikey()

    # Authentication TODO get responding apikey for each user.0
    headers = {
        'X-username': username,
        'X-apikey': api_key,
        'Content-Type' : 'application/json; charset=utf-8',
    }

    private_key_hex = key_manager.return_private_key()
    # # Generate a new random signing key / private key generation and converting to json format
    signing_key = nacl.signing.SigningKey(private_key_hex, encoder=nacl.encoding.HexEncoder)

    # #public pair / converting to json
    # verify_key = signing_key.verify_key
    # verify_key_hex_str =  verify_key.encode(nacl.encoding.HexEncoder).decode('utf-8')
    
    login_server_record = server_api.get_loginserver_record(username)

    time_creation = str(time())

    
    #sign the message, which is the public + name
    message_bytes = bytes(login_server_record+message+time_creation, encoding='utf-8')
    signed = signing_key.sign(message_bytes, encoder=nacl.encoding.HexEncoder)
    signature_hex_str = signed.signature.decode('utf-8')


    payload = {
        "loginserver_record" : login_server_record,
        "message" : message,
        "sender_created_at" : time_creation,
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
        print(" Error in rx_broadcast")
        print(error.read())
        exit()

    response_dict = json.loads(data.decode(encoding))
    return(response_dict)

print(broadcast("mche226","hello"))
def privatemessage (username,target_username,message):
    """ Use this API to transmit a secret message between users. 
    'Meta' information is public, the message itself is private """
    list = server_api.list_users(username)
    # Target connection address
    connection_address = helper_modules.get_connection_address(list,target_username)
    # find targer pubkey
     
    target_pubkey_str = helper_modules.get_pubkey(list,target_username)
    target_pubkey_bytes = bytes(target_pubkey_str,encoding='utf-8')

    url = "http://" + connection_address + "/api/rx_privatemessage"    
    
    api_key = key_manager.return_apikey()
    headers = {
        'X-username': username,
        'X-apikey': api_key,
        'Content-Type' : 'application/json; charset=utf-8',
    }
    
    login_server_record = server_api.get_loginserver_record(username)

    # Encryption of the message 
    message_b = bytes(message,encoding = 'utf-8')
    verifykey = nacl.signing.VerifyKey(target_pubkey_bytes, encoder = nacl.encoding.HexEncoder)
    publickey = verifykey.to_curve25519_public_key()
    sealed_box = nacl.public.SealedBox(publickey)
    encrypted = sealed_box.encrypt(message_b, encoder = nacl.encoding.HexEncoder)

    sender_created_at = str(time())
    #signing key 
    private_key_hex_bytes = key_manager.return_private_key()
    signing_key = nacl.signing.SigningKey(private_key_hex_bytes,nacl.encoding.HexEncoder)
    signature_bytes = bytes(login_server_record+target_pubkey_str+target_username+ encrypted.decode('utf-8') +sender_created_at,encoding = 'utf-8')
    signature = signing_key.sign(signature_bytes,encoder=nacl.encoding.HexEncoder)
    payload = {
        "loginserver_record":login_server_record,
        "target_pubkey" : target_pubkey_str,
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
    
    response_dict = json.loads(data.decode(encoding))
    return (response_dict)