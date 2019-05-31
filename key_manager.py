
def return_private_key():
    # open database
    # check database
    """Reads the keys file and returns the private key"""
    file = open("keys.txt", "r")
    file_lines = file.readline()
    file.close()    
    return str.encode(file_lines)


def write_apikey(apikey):
    """ Writes the new api key into a text file"""
    file = open("api_keys.txt", "w+")
    file.write(apikey)
    file.close()


def return_apikey():
    """ Reads the first line of the api_key text file"""
    file = open("api_keys.txt","r")
    file_lines = file.readline()
    file.close()    
    return (file_lines)
