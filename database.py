import sqlite3
from server_api import list_users

def add_accounts_data(username,pubkey,ip_address,connection_type,connection_updated_at,status):
    """ Adds any new information to the accounts table in the database"""
    # make the connection to the database
    conn = sqlite3.connect('database.db')
    # cursor
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
    for user in list_of_users:
        username = user['username']
        pubkey = user['incoming_pubkey']
        ip_address = user['connection_address']
        connection_type = user['connection_location']
        connection_updated_at = user['connection_updated_at']
        status = user['status']
        add_accounts_data(username,pubkey,ip_address,connection_type,connection_updated_at,status)
    
    

update_accounts_data("mche226","gWDjcnEIt3gwkKDXS2ac")
