import urllib.request
import json
import base64
import nacl.encoding
import nacl.signing
import nacl.pwhash
import nacl.utils
import nacl.secret
from time import time
import key_manager
from helper_modules import get_ip,send_data,get_port,get_connect_location,get_external_ip,get_internal_port

    
def load_api_key(username,password):
    """ Gets new API key from server , used for this session. \n
    This needs to be done before creating the user object"""
    url = "http://cs302.kiwi.land/api/load_new_apikey"

    credentials = ('%s:%s' % (username, password))
    b64_credentials = base64.b64encode(credentials.encode('ascii'))
    headers = {
        'Authorization': 'Basic %s' % b64_credentials.decode('ascii'),
        'Content-Type' : 'application/json; charset=utf-8',
    }

    response = send_data(url,headers)

    # checks if the returned value is a proper response or indicate where the error has occured
    if isinstance(response,dict):
        return response
    else:
        print("Error in load_api_key")
        return False


def loginserver_pubkey():
    """ Return the public key of the login server, which may be used to validate
        loginserver_records in broadcasts / private messages """
    url = "http://cs302.kiwi.land/api/loginserver_pubkey"
    response = send_data(url)
    # checks if the returned value is a proper response or indicate where the error has occured
    if isinstance(response,dict):
        return(response['pubkey'])
    else:
        print("Error in loginserver_pubkey")


def get_loginserver_record(username,api_key):
    """ Use this API to load your current loginserver_record for use in creating
    point-to-point messages. Change it by creating new pubkeys with /api/add_pubkey and/or by
    changing the current pubkey in /api/report."""
    url = "http://cs302.kiwi.land/api/get_loginserver_record"
    
    headers = {
        'X-username': username,
        'X-apikey': api_key,
        'Content-Type' : 'application/json; charset=utf-8',
    }

    response = send_data(url,headers)
    if isinstance(response,dict):
        return response['loginserver_record']
    else:
        print("Error in get_loginserver_record")


def add_privatedata (username,api_key,priv_password,private_data,private_key_str):
    """Use this API to save symmetrically encrypted private data for a given user. It will
    automatically delete previously uploaded private data. """

    if (len(private_data) != 6):
        raise IndexError('Private data list does not have the right amount of data. Need 6 lists')
        
    # Authentication
    url = "http://cs302.kiwi.land/api/add_privatedata"
    headers = {
        'X-username': username,
        'X-apikey': api_key,
        'Content-Type' : 'application/json; charset=utf-8',
    }
    
    # Private data
    prikeys=private_data[0]
    blocked_pubkeys= private_data[1]
    blocked_usernames= private_data[2]
    blocked_words= private_data[3]
    favourite_message_signature= private_data[4]
    friends_usernames= private_data[5]

    # Generating Payload
    private_data = {
        "prikeys": prikeys,
        "blocked_pubkeys": blocked_pubkeys,
        "blocked_usernames":blocked_usernames,
        "blocked_words":blocked_words,
        "favourite_message_signature":favourite_message_signature,
        "friends_usernames":friends_usernames,
    }
    private_data_json = json.dumps(private_data)
    private_data_json_bytes = private_data_json.encode('utf-8')
    # Signing key
    signing_key = nacl.signing.SigningKey(private_key_str, encoder= nacl.encoding.HexEncoder)
    # Login server record
    loginserver_record_str = get_loginserver_record(username,api_key)
    # Time stamp
    client_saved_at = str(time())
    
    # Secret box generation
    # Creating symmetric key
    priv_password_b = priv_password.encode('utf-8')
    # Obtaining the salt
    salt = (priv_password_b * 16)[0 : 16]
    # Generate symetric key and use it for a secret box6
    priv_pass_key = nacl.pwhash.argon2i.kdf(32,priv_password_b,salt,8,536870912,encoder=nacl.encoding.HexEncoder)
    priv_box = nacl.secret.SecretBox(priv_pass_key, encoder = nacl.encoding.HexEncoder)

    #Encypting payload
    nonce = nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)
    encrypted_private_data = priv_box.encrypt(private_data_json_bytes,nonce)

    # Convert to b64 for transmission
    encrypted_private_data_str = base64.b64encode(encrypted_private_data).decode('utf-8')

    # Signature
    signature_message_bytes = bytes(encrypted_private_data_str + loginserver_record_str + client_saved_at,encoding='utf-8')
    signature = signing_key.sign(signature_message_bytes,encoder=nacl.encoding.HexEncoder)
    signature_hex_str = signature.signature.decode('utf-8')
    
    # Actual paylod
    payload = {
        "privatedata" : encrypted_private_data_str,
        "loginserver_record" : loginserver_record_str,
        "client_saved_at" : client_saved_at,
        "signature" : signature_hex_str
    }
    
    payload_str = json.dumps(payload)
    payload_data = payload_str.encode('utf-8')
    
    # sending the data
    response = send_data(url,headers,payload_data)
    if isinstance(response,dict):
        return response
    else: 
        print("Error in add_privatedata")    

# privatedata = [["ecd0f760d4787ac45aea7e4e905c445a3fd6323b3af4871fc1ed6d5f1662cab2"],['blockedpubkey1'],["blockeduser1","blockeduser2"],['blockedwords'],["fav sign"],['friends']]
# print(add_privatedata('mche226','jV2KJb7lImzUs3Lqz2l5','dognuts',privatedata,'ecd0f760d4787ac45aea7e4e905c445a3fd6323b3af4871fc1ed6d5f1662cab2'))

def get_privatedata(username,api_key,priv_password):
    """ Use this API to load the saved symmetrically encrypted private data for a user. Enter private password """
    url = "http://cs302.kiwi.land/api/get_privatedata"

    headers = {
        'X-username': username,
        'X-apikey': api_key,
        'Content-Type' : 'application/json; charset=utf-8',
    }
    response = send_data(url,headers)

    if isinstance(response,dict):
        try:
            # get the encypted data
            encypted_private_data  = response ['privatedata']
            encypted_private_data_bytes = base64.b64decode(encypted_private_data.encode('utf-8'))
            #use password to decrypt the box
            priv_password_b = priv_password.encode('utf-8')
            salt = (priv_password_b * 16)[0 : 16]
            priv_pass_key = nacl.pwhash.argon2i.kdf(32,priv_password_b,salt,8,536870912,encoder=nacl.encoding.HexEncoder)
            priv_box = nacl.secret.SecretBox(priv_pass_key,encoder=nacl.encoding.HexEncoder)
            decrypted_private_data = priv_box.decrypt(encypted_private_data_bytes).decode('utf-8')
            # Convert the str to a dictionary for ease of operation
            decrypted_private_data_dict = json.loads(decrypted_private_data)
            return decrypted_private_data_dict
        except  Exception as error:
            print (error)
# print(get_privatedata('mche226',"jV2KJb7lImzUs3Lqz2l5","dognuts"))

def report(username,api_key,private_key_str,status = 'online'):
    """ Informs login server about connection information. 
    Call this at least once every 5 minutes and at most once
    every 30 seconds. Optional status 'online, 'away', 'busy', 'offline'"""
    url = "http://cs302.kiwi.land/api/report"
    
    headers = {
        'X-username': username,
        'X-apikey': api_key,
        'Content-Type' : 'application/json; charset=utf-8',
    }
   
    # Grab the private key
    private_key_hex_b = bytes(private_key_str,encoding = 'utf-8')
    signing_key = nacl.signing.SigningKey(private_key_hex_b, encoder=nacl.encoding.HexEncoder)
    # Get the verify key from that
    verify_key = signing_key.verify_key
    verify_key_hex_str =  verify_key.encode(nacl.encoding.HexEncoder).decode('utf-8')

    # Connection Address
    # For use at uni
    connection_address = get_ip()
    # For use outside uni. Requires port forward
    # connection_address = get_external_ip()
    listening_port = str(get_internal_port())
    connection_location = str(get_connect_location())

    payload = {
        "connection_location": connection_location,
        "connection_address": connection_address+":"+listening_port,
        "incoming_pubkey" : verify_key_hex_str,
        "status" : status
    }

    payload_str = json.dumps(payload)
    payload_data = payload_str.encode('utf-8')

    response = send_data(url,headers,payload_data)
    if isinstance(response,dict):
        return response
    else: 
        print("Error in reporting")

def new_key():
    """ Generates a new pair of keys and saves the private key hex"""
    # generate new keypair
    new_key_hex_str = nacl.signing.SigningKey.generate().encode(encoder = nacl.encoding.HexEncoder).decode('utf-8')
    return new_key_hex_str




def add_pubkey(username,api_key,private_key_str):
    """Associate a public key with your account. This key pair is used for signing
    returns the response as a dict"""

    url = "http://cs302.kiwi.land/api/add_pubkey"
    
 
    # use existing keypair 
    private_key_hex_bytes = bytes(private_key_str,encoding='utf-8')
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
    signature = signing_key.sign(message_bytes, encoder=nacl.encoding.HexEncoder)
    signature_hex_str = signature.signature.decode('utf-8')

    payload = {
        "pubkey": verify_key_hex_str,
        "username": username,
        "signature": signature_hex_str,
    }

    payload_str = json.dumps(payload)
    payload_data = payload_str.encode('utf-8')

    response = send_data(url,headers,payload_data)
    if isinstance(response,dict):
        return response
    else:
        print("Error in adding pubkey")


def check_pubkey(username, api_key, verify_key_hex_str = "b9eba910b59549774d55d3ce49a7b4d46ab5e225cdcf2ac388cf356b5928b6bc"):
    """ Use this API to load the loginserver record for a given public key. \n 
    TODO get rid of default verifykey"""
    # Authentication
    headers = {
        'X-username': username,
        'X-apikey': api_key,
        'Content-Type' : 'application/json; charset=utf-8',
    }

    url = "http://cs302.kiwi.land/api/check_pubkey?pubkey=" + verify_key_hex_str

    response = send_data(url,headers)
    if isinstance(response,dict):
        return response
    else:
        print("error in checking pubkey")


def list_users(username,api_key):
    """ Lists current active users from login server"""
    url = "http://cs302.kiwi.land/api/list_users"
    
    headers = {
        'X-username': username,
        'X-apikey': api_key,
        'Content-Type' : 'application/json; charset=utf-8',
    }
    response = send_data(url=url,headers=headers)
    if isinstance(response,dict):
        return response['users']
    else:
        print("Error in listing users")

# print(list_users('mche226','zTbpbfXfBMa6rgizC7QN'))
def ping (username,api_key,private_key_str):
    """Calls the API ping and returns the response as a dictionary"""

    url = "http://cs302.kiwi.land/api/ping"
    headers = {
        'X-username': username,
        'X-apikey': api_key,
        'Content-Type' : 'application/json; charset=utf-8',
    }
    
    # reads the stored key and uses that
    private_key_hex_bytes = bytes(private_key_str,encoding = 'utf-8')

    # Uses the stored signing key hex bytes to reconstruct the key pair. 
    signing_key = nacl.signing.SigningKey(private_key_hex_bytes, encoder=nacl.encoding.HexEncoder)
    # Getting the public key 
    verify_key = signing_key.verify_key
    verify_key_hex_bytes = verify_key.encode(nacl.encoding.HexEncoder)
    verify_key_hex_str =  verify_key_hex_bytes.decode('utf-8')

    # Sign the message, which is the public key
    signed = signing_key.sign(verify_key_hex_bytes, encoder=nacl.encoding.HexEncoder)
    signature_hex_str = signed.signature.decode('utf-8')

    payload = {
        "pubkey" :verify_key_hex_str ,
        "signature" : signature_hex_str,
    }
    
    payload_str = json.dumps(payload)
    payload_data = payload_str.encode('utf-8')

    response = send_data(url=url,headers=headers,data=payload_data)
    if isinstance(response,dict):
        return response
    else:
        print("error in ping")
