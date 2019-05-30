
def return_private_key():
    """Reads the keys file and returns the private key"""
    file = open("keys.txt", "r")
    file_lines = file.readline()
    file.close()    
    return str.encode(file_lines)

