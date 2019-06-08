import sqlite3
from server_api import list_users
import nacl.encoding
import nacl.signing
import nacl.public
import nacl.utils
import nacl.secret
from key_manager import return_private_key


###
# Accounts table
###
def add_accounts_data(username,pubkey,ip_address,connection_type,connection_updated_at,status):
    """ Adds any new information to the accounts table in the database"""
    # make the connection to the database
    conn = sqlite3.connect('database.db')
    # cursor+
    c = conn.cursor()
    # checks if username exists
    c.execute("""SELECT username , pubkey, ip_address FROM Accounts WHERE username = ?""",[username])
    rows = c.fetchall()
    # try to update the database, prints any errors
    try:
        if len(rows) == 0:
            # adds the data
            data = (username,pubkey,ip_address,connection_type,connection_updated_at,status)
            c.execute("""insert into Accounts (username,pubkey,ip_address,connection_type,connection_updated_at,status) VALUES(?,?,?,?,?,?)""",data)
        else:
            # if exists update the values 
            data = (pubkey,ip_address,connection_type,connection_updated_at,status,username)
            c.execute("UPDATE Accounts SET pubkey = ? , ip_address = ?,connection_type = ?, connection_updated_at = ?, status = ? WHERE username = ?", data)
    except Exception as e:
        print(e)
    # commit
    conn.commit()
    # close the connection 
    conn.close()


def update_accounts_data(username,api_key):
    """ Updates all the accounts details into the database"""
    list_of_users = list_users(username,api_key)
    try:
        for user in list_of_users:
            username = user['username']
            pubkey = user['incoming_pubkey']
            ip_address = user['connection_address']
            connection_type = user['connection_location']
            connection_updated_at = user['connection_updated_at']
            status = user['status']
            add_accounts_data(username,pubkey,ip_address,connection_type,connection_updated_at,status)
    except TypeError as e:
        print(e)


def get_target_pubkey(target_username):
    """ Given a target user name, find their pubkey and ip address from the database \n
        returns empty list if can't find. make sure to catch this"""
    # make the connection
    conn = sqlite3.connect('database.db')
    #cursor
    c = conn.cursor()
    # Try to find pubkey
    c.execute("SELECT pubkey FROM accounts WHERE username =?", [target_username])
    pubkey = c.fetchone()
    # Commit
    conn.commit()
    # Close the connection
    conn.close()
    return pubkey[0]
    

###
# Private Message Table
###
def add_private_message(loginserver_record,target_pubkey,target_username,encrypted_message,sender_created_at,sender):
    """ Adds the private message into the database"""
    pass
    

def get_sender_loginserver_record(loginserver_record):
    """ Takes the login server record and returns the first element which should be the user. """
    try:
        loginserver_record_list = loginserver_record.split(",")
        return (loginserver_record_list[0])
    except Exception as e:
        print( "Loginserver Record format error. Unable to get sender")
        print (e)



def decrypt_private_message(message,priv_key_hex):
    """ Decryptes the private message using their private key"""
    message_b= bytes(message,encoding = 'utf-8')
    # get the private key string
    # priv_key_hex = return_private_key()
    # Reconstruct key
    signing_key = nacl.signing.SigningKey(priv_key_hex, encoder= nacl.encoding.HexEncoder)
    private_key = signing_key.to_curve25519_private_key()
    
    unseal_box = nacl.public.SealedBox(private_key)
    decrypted = unseal_box.decrypt(message_b,encoder= nacl.encoding.HexEncoder)
    return (decrypted.decode('utf-8'))
