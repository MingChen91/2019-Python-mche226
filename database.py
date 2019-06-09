import sqlite3
import nacl.encoding
import nacl.signing
import nacl.public
import nacl.utils
import nacl.secret
import json
import helper_modules
from server_api import list_users
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
    # changes all status to offline because some people dont report offline
    
    list_of_users = list_users(username,api_key)

    # if can't list users dont wipe the existing database
    if list_of_users != None:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("UPDATE Accounts set status = 'offline'")
        conn.commit()
        conn.close()
    
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

# update_accounts_data('mche226','TTQnPwGsohwb5ae1H8tq')

def get_target_pubkey(target_username):
    """ Given a target user name, find their pubkey and ip address from the database \n
        returns empty list if can't find. make sure to catch this(?)"""
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


def get_online_users():
    """ Fetches all the users with online as status in a dict , use this as the list of people to message"""
    conn = sqlite3.connect('database.db')
    #cursor
    c = conn.cursor()
    # Try to find pubkey
    c.execute("SELECT username,pubkey,ip_address,connection_type,connection_updated_at,status from accounts where status = 'online' order by username ASC ")
    list_of_users = c.fetchall()
    
    # Commit
    conn.commit()
    # Close the connection
    conn.close()
    return list_of_users


def get_all_users():
    """ Returns all the status and name of all users in database and their pingcheck status"""
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    # Obtain the username pubkey and ipaddress for "online" users or anyone I have ping checked
    c.execute("SELECT username,status from accounts order by status ASC, username ASC")
    online_list = c.fetchall()
    online_dict =[]
    # construct the dictionary
    for row in online_list:
        online_dict.append({'username':row[0],'status':row[1]})
    # close connection to database
    conn.commit()
    conn.close()
    return online_dict


###
# Private Message Table
###
def add_private_message(loginserver_record,target_pubkey,target_username,encrypted_message,sender_created_at,signature,self_copy):
    """ Adds the private message into the database"""
    conn = sqlite3.connect('database.db')
    # cursor
    c = conn.cursor()
    # insert data
    sender = loginserver_record.split(',')[0]
    data = (loginserver_record,target_pubkey,target_username,encrypted_message,sender_created_at,sender,signature,self_copy)
    c.execute("""INSERT INTO private_message (loginserver_record,target_pubkey,target_username,encrypted_message,sender_created_at,sender,signature,self_copy) VALUES (?,?,?,?,?,?,?,?)""",data)
    # commit
    conn.commit()
    # close the connection 
    conn.close()
    

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


###
# Broadcast Message Table
##

def add_broadcast_message(loginserver_record,message,sender_created_at,signature):
    # Add broadcasted message into my database
    conn = sqlite3.connect('database.db')
    # cursor
    c = conn.cursor()
    # insert data
    data = (loginserver_record,message,sender_created_at,signature)
    c.execute("""INSERT INTO broadcast_message (loginserver_record,message,sender_created_at,signature) VALUES (?,?,?,?)""",data)
    # commit
    conn.commit()
    # close the connection 
    conn.close()


def get_broadcast_message():
    """ Fetches all broadcasted in database messages"""
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT loginserver_record,message,sender_created_at,signature FROM broadcast_message ORDER by sender_created_at DESC")
    broadcast_list = c.fetchall()
    # TODO block things
    
    # Commit
    conn.commit()
    # Close the connection
    conn.close()
    
    broadcast_dict=[]
    # form into dictionary
    for row in broadcast_list:
        loginserver_record = row[0].split(',')
        sender_created_at = helper_modules.convert_time(row[2])
        broadcast_dict.append({'username':loginserver_record[0],'message':row[1],'sender_created_at':sender_created_at})

    return(broadcast_dict)
