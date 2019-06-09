import urllib.request
import json
import nacl.encoding
import nacl.signing
from time import time
from server_api import get_loginserver_record
from helper_modules import send_data,get_ip,get_port,get_connect_location
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
        print('Broadcast ok')
        return response
    else: 
        print("Error in broadcasting to " + ip_address)
        return False


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


def tx_ping_check(connection_address):
    """ Use this to call other people's ping check to see if you can establish a valid connection \n
        returns True or False depending on if connection is successful"""
    url = "http://" + connection_address + "/api/ping_check"
    headers = {
        'Content-Type' : 'application/json; charset=utf-8',
    }
    # payload information
    my_time = str(time())
    connection_address = get_ip() +":"+ str(get_port())
    connection_location = get_connect_location()

    payload = {
        "my_time" : my_time,
        "connection_address":connection_address,
        "my_active_usernames":"n/a",
        "connection_location":connection_location
    }
    payload_data = json.dumps(payload).encode('utf-8')

    response = send_data(url,headers = headers,data=payload_data)
    
    try:
        if (response['response'] == 'ok'):
            return True
    except:
        return False


def broadcast_to_all(username,api_key,priv_key_hex_str,message):
    """ Broadcast to all users that are online"""
    list_of_users = database.get_online_users()
    # print(list_of_users)
    for users in list_of_users:
        print('broadcasting to: ' +users[0])
        if users[0] == 'admin':
            continue
        ip = users[2]
        tx_broadcast(username,api_key,priv_key_hex_str,ip,message)


def private_message_all(username,api_key,target_username,priv_key_hex_bytes,message):
    """send copies of private message to everyone online, except for self, add one into database directly along with a copy signed by myself"""
    list_of_users = database.get_online_users()
    # print(list_of_users)
    for users in list_of_users:
        print('private messaging to: ' + users[0])
        connection_address = users[2]
        tx_privatemessage (username,api_key,target_username,priv_key_hex_bytes,message,connection_address)

    # reconstruct pubkey to yourself
    sing
    # add signed version by yourself 