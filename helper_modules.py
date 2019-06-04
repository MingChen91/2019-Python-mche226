import socket
# import urllib.request

def get_ip():
    """ Returns public IP by getting it from ident.me """
    # if identme is down, use the commented code. which only gets local IP. sometimes different to public ip
    # external_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')
    # return external_ip

    """ Returns the local IP"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


def get_pubkey(user_list_dict,target_username):
    """ Find the public key for a given user name, using the current list users\n
    TODO better error handling"""

    user_list = user_list_dict['users']
    for users in user_list:
        if users['username'] == target_username: 
            return users['incoming_pubkey']
    print("GET PUBKEY CAN'T FIND USER")
    return None


def get_connection_address(user_list_dict,target_username):
    """ Find the IP address for a given user name, using the current list users \n
    TODO better error handling"""
   
    user_list = user_list_dict['users']
    for users in user_list:
        if users['username'] == target_username:
            return users['connection_address']
    print("GET CONNECTION ADDRESS CAN'T FIND USER")
    return None
