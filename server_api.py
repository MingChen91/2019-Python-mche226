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
        return False

    response_dict = json.loads(data.decode(encoding))
    key_manager.write_apikey(response_dict['api_key'])
    # print(response_dict)
    if response_dict['response'] == 'ok':
        return True
    else:
        return False


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
    blocked_words= ["penis","dickhead"]
    favourite_message_signature= []
    friends_usernames= []

    # Uses the stored signing key hex bytes to reconstruct the key pair. 
    signing_key = nacl.signing.SigningKey(private_key_hex_str, encoder=nacl.encoding.HexEncoder)
    loginserver_record_str = get_loginserver_record(username)
    client_saved_at = str(time())
    private_data = {
        "prikeys": [],#[private_key_hex_str],
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


def get_privatedata(username):
    """ Use this API to load the saved symmetrically encrypted private data for a user. """
    url = "http://cs302.kiwi.land/api/get_privatedata"
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
        print("Error from get_privatedata")
        print(error.read())
        exit()

    response_dict = json.loads(data.decode(encoding))
    return(response_dict)


def report(username,status = 'online'):
    """ Informs login server about connection information. 
    Call this at least once every 5 minutes and at most once
    every 30 seconds. Optional status 'online, 'away', 'busy', 'offline'"""

    url = "http://cs302.kiwi.land/api/report"
    api_key = key_manager.return_apikey()
    headers = {
        'X-username': username,
        'X-apikey': api_key,
        'Content-Type' : 'application/json; charset=utf-8',
    }

    private_key_hex = key_manager.return_private_key()
    
    # Grab the private key
    signing_key = nacl.signing.SigningKey(private_key_hex, encoder=nacl.encoding.HexEncoder)
    # Get the verify key from that
    verify_key = signing_key.verify_key
    verify_key_hex_str =  verify_key.encode(nacl.encoding.HexEncoder).decode('utf-8')

    # Connection Address 
    connection_address = get_ip()
    # listening port hard coded atm. TODO grab this from cherrypy server later
    listening_port = ":1234"
    # Conection_location TODO DO I NEED TO CHANGE THIS DYNAMICALLY?
    connection_location = "2'"
    payload = {
        "connection_location": connection_location,
        "connection_address": connection_address+listening_port,
        "incoming_pubkey" : verify_key_hex_str,
        "status" : status
    }

    payload_str = json.dumps(payload)
    payload_data = payload_str.encode('utf-8')

    try:
        req = urllib.request.Request(url, data=payload_data, headers=headers)
        response = urllib.request.urlopen(req)
        data = response.read() # read the received bytes
        encoding = response.info().get_content_charset('utf-8') #load encoding if possible (default to utf-8)
        response.close()
    except urllib.error.HTTPError as error:
        print("Error in report")
        print(error.read())
        exit()

    response_dict = json.loads(data.decode(encoding))
    return(response_dict)


def add_pubkey(username):
    """Associate a public key with your account. This key pair is used for signing
    returns the response as a dict"""

    url = "http://cs302.kiwi.land/api/add_pubkey"
    
    # generate new keypair
    # new_key = nacl.signing.SigningKey.generate()
    # use existing keypair 
    private_key_hex_bytes = key_manager.return_private_key()
    api_key = key_manager.return_apikey()
    headers = {
        'X-username': username,
        'X-apikey': api_key,
        'Content-Type' : 'application/json; charset=utf-8',
    }

    # Uses the stored signing key hex bytes to reconstruct the key pair. 
    signing_key = nacl.signing.SigningKey(private_key_hex_bytes, encoder=nacl.encoding.HexEncoder)
    # Getting the public key
    verify_key = signing_key.verify_key
    # Convert to bytes, then decode to string
    verify_key_hex_str = verify_key.encode(nacl.encoding.HexEncoder).decode('utf-8')
    # Message is verify key + username
    message_bytes = bytes(verify_key_hex_str + username, encoding='utf-8')
    # Sign the message, which is the public + name
    signed = signing_key.sign(message_bytes, encoder=nacl.encoding.HexEncoder)
    signature_hex_str = signed.signature.decode('utf-8')

    payload = {
        "pubkey": verify_key_hex_str,
        "username": username,
        "signature": signature_hex_str,
    }

    payload_str = json.dumps(payload)
    payload_data = payload_str.encode('utf-8')

    try:
        # report
        req = urllib.request.Request(url, data=payload_data, headers=headers)
        response = urllib.request.urlopen(req)
        data = response.read()  # read the received bytes
        # load encoding if possible (default to utf-8)
        encoding = response.info().get_content_charset('utf-8')
        response.close()

    except urllib.error.HTTPError as error:
        print("Error in add pubkey")
        print(error.read())
        exit()

    response_dict = json.loads(data.decode(encoding))
    return response_dict


def check_pubkey(username, verify_key_hex_str = "b9eba910b59549774d55d3ce49a7b4d46ab5e225cdcf2ac388cf356b5928b6bc"):
    """ Use this API to load the loginserver record for a given public key. \n 
    TODO get rid of default verifykey"""
    # Authentication
    api_key = key_manager.return_apikey()
    headers = {
        'X-username': username,
        'X-apikey': api_key,
        'Content-Type' : 'application/json; charset=utf-8',
    }

    url = "http://cs302.kiwi.land/api/check_pubkey?pubkey=" + verify_key_hex_str

    try:
        # report
        req = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(req)
        data = response.read() # read the received bytes
        encoding = response.info().get_content_charset('utf-8') #load encoding if possible (default to utf-8)
        response.close()
        
    except urllib.error.HTTPError as error:
        print(error.read())
        exit()

    response_dict = json.loads(data.decode(encoding))
    return(response_dict)


def list_users(username):
    """ Lists current active users from login server"""
    url = "http://cs302.kiwi.land/api/list_users"
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
        print(error.read())
        exit()

    response_dict = json.loads(data.decode(encoding))
    return(response_dict)


def ping (username):
    """Calls the API ping and returns the response as a dictionary"""

    url = "http://cs302.kiwi.land/api/ping"
    api_key = key_manager.return_apikey()
    headers = {
        'X-username': username,
        'X-apikey': api_key,
        'Content-Type' : 'application/json; charset=utf-8',
    }
    
    # reads the stored key and uses that
    private_key_hex_bytes = key_manager.return_private_key()

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

print(ping("mche226"))