import urllib.request
import json
import base64
import nacl.encoding
import nacl.signing
from time import time
import key_manager
from helper_modules import get_ip

def load_api_key(username,password):
    """ Gets new API key from server , used for this session"""
    url = "http://cs302.kiwi.land/api/load_new_apikey"

    credentials = ('%s:%s' % (username, password))
    b64_credentials = base64.b64encode(credentials.encode('ascii'))
    headers = {
        'Authorization': 'Basic %s' % b64_credentials.decode('ascii'),
        'Content-Type' : 'application/json; charset=utf-8',
    }

    try:
        req = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(req)
        data = response.read() # read the received bytes
        encoding = response.info().get_content_charset('utf-8') #load encoding if possible (default to utf-8)
        response.close()
    except urllib.error.HTTPError as error:
        print("Error from load_api_keys.")
        print(error.read())
        exit()

    response_dict = json.loads(data.decode(encoding))
    key_manager.write_apikey(response_dict['api_key'])
    return(response_dict)


def loginserver_pubkey():
    """ Return the public key of the login server, which may be used to validate
        loginserver_records in broadcasts / private messages """
    url = "http://cs302.kiwi.land/api/loginserver_pubkey"

    try:
        req = urllib.request.Request(url)
        response = urllib.request.urlopen(req)
        data = response.read() # read the received bytes
        encoding = response.info().get_content_charset('utf-8') #load encoding if possible (default to utf-8)
        response.close()
    except urllib.error.HTTPError as error:
        print("Error from loginserver_pubkey.")
        print(error.read())
        exit()

    response_dict = json.loads(data.decode(encoding))
    return(response_dict)


def get_loginserver_record(username):
    """ Use this API to load your current loginserver_record for use in creating
    point-to-point messages. Change it by creating new pubkeys with /api/add_pubkey and/or by
    changing the current pubkey in /api/report."""
    url = "http://cs302.kiwi.land/api/get_loginserver_record"
    api_key = key_manager.return_apikey()

    headers = {
        'X-username': username,
        'X-apikey': api_key,
        'Content-Type' : 'application/json; charset=utf-8',
    }

    try:
        req = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(req)
        data = response.read() # read the received bytes
        encoding = response.info().get_content_charset('utf-8') #load encoding if possible (default to utf-8)
        response.close()
    except urllib.error.HTTPError as error:
        print("Error occured in get_loginserver_record")
        print(error.read())
        exit()

    response_dict = json.loads(data.decode(encoding))
    return(response_dict["loginserver_record"])


def add_privatedata (username):
    """Use this API to save symmetrically encrypted private data for a given user. It will
    automatically delete previously uploaded private data.
    
    TODO
    --NEED TO IMPLEMENT ENCRYPTION FOR PRIVATE DATA--
    """
    # Authentication
    url = "http://cs302.kiwi.land/api/add_privatedata"
    api_key = key_manager.return_apikey()
    headers = {
        'X-username': username,
        'X-apikey': api_key,
        'Content-Type' : 'application/json; charset=utf-8',
    }
    # Private Data TODO from database
    private_key_hex_str = key_manager.return_private_key().decode('utf-8')
    blocked_pubkeys= []
    blocked_usernames= []
    blocked_words= []
    favourite_message_signature= []
    friends_usernames= []

    # Uses the stored signing key hex bytes to reconstruct the key pair. 
    signing_key = nacl.signing.SigningKey(private_key_hex_str, encoder=nacl.encoding.HexEncoder)
    loginserver_record_str = get_loginserver_record(username)
    client_saved_at = str(time())
    private_data = {
        "prikeys": [private_key_hex_str],
        "blocked_pubkeys": blocked_pubkeys,
        "blocked_usernames":blocked_usernames,
        "blocked_words":blocked_words,
        "favourite_message_signature":favourite_message_signature,
        "friends_usernames":friends_usernames,
    }

    private_data_json = json.dumps(private_data)
    signature_bytes = bytes(private_data_json + loginserver_record_str + client_saved_at,encoding='utf-8')
    signature = signing_key.sign(signature_bytes,encoder=nacl.encoding.HexEncoder)
    signature_hex_str = signature.signature.decode('utf-8')

    payload = {
        "privatedata" : private_data_json,
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
        print("Error from adding private data.")
        print(error.read())
        exit()

    response_dict = json.loads(data.decode(encoding))
    return response_dict

print(add_privatedata("Mche226"))