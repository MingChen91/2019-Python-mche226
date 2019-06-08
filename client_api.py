import urllib.request
import json
import nacl.encoding
import nacl.signing
from time import time
from server_api import get_loginserver_record
from helper_modules import send_data
import server_api
import database

from key_manager import return_private_key

def tx_broadcast(username,api_key,priv_key_hex,ip_address,message = "Default Message"):
    """ Use this api to transmit a signed broadcast between users. """
    # Address to send to
    url = "http://"+ip_address+"/api/rx_broadcast"
    # Authentication 
    headers = {
        'X-username': username,
        'X-apikey': api_key,
        'Content-Type' : 'application/json; charset=utf-8',
    }
    # payload 
    login_server_record = get_loginserver_record(username,api_key)
    time_creation = str(time())
    
    # Signing the message
    message_bytes = bytes(login_server_record+message+time_creation, encoding='utf-8')
    signing_key = nacl.signing.SigningKey(priv_key_hex, encoder=nacl.encoding.HexEncoder)
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

    # send the data
    response = send_data(url, headers, payload_data)
    if isinstance(response,dict):
        return response
    else: 
        print("Error in broadcasting to " + ip_address)


def tx_privatemessage (username,api_key,target_username,priv_key_hex_bytes,message,connection_address):
    """ Use this API to transmit a secret message between users. 
    'Meta' information is public, the message itself is private """
       # address to send to 
    url = "http://" + connection_address + "/api/rx_privatemessage"    
    
    headers = {
        'X-username': username,
        'X-apikey': api_key,
        'Content-Type' : 'application/json; charset=utf-8',
    }
    
    # Payload data
    login_server_record = get_loginserver_record(username,api_key)
    sender_created_at = str(time())
    # find targer pubkey
    target_pubkey_str = database.get_target_pubkey(target_username)
    target_pubkey_bytes = bytes(target_pubkey_str,encoding='utf-8')
    
    # Encryption of the message 
    message_b = bytes(message,encoding = 'utf-8')
    verifykey = nacl.signing.VerifyKey(target_pubkey_bytes, encoder = nacl.encoding.HexEncoder)
    publickey = verifykey.to_curve25519_public_key()
    sealed_box = nacl.public.SealedBox(publickey)
    encrypted = sealed_box.encrypt(message_b, encoder = nacl.encoding.HexEncoder)
    encrypted_message = encrypted.decode('utf-8')

    #signing message
    signing_key = nacl.signing.SigningKey(priv_key_hex_bytes,nacl.encoding.HexEncoder)
    signature_bytes = bytes(login_server_record+target_pubkey_str+target_username+ encrypted.decode('utf-8') +sender_created_at,encoding = 'utf-8')
    signature = signing_key.sign(signature_bytes,encoder=nacl.encoding.HexEncoder)
    signature_str = signature.signature.decode('utf-8')
        
    payload = {
        "loginserver_record":login_server_record,
        "target_pubkey" : target_pubkey_str,
        "target_username" : target_username,
        "encrypted_message":encrypted_message,
        "sender_created_at": sender_created_at,
        "signature": signature_str
    }
    
    payload_str = json.dumps(payload)
    payload_data = payload_str.encode('utf-8')

    response = send_data(url,headers,payload_data)
    if isinstance(response,dict):
        return response
    else: 
        print("Error in private message to " + target_username)

# print(privatemessage("mche226","BSnjWCHxtYwBBONOzZW2","tche614",return_private_key(),"😁","172.23.61.246:1234"))