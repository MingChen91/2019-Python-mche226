f = open("keys.txt", "w+")
f.write("ecd0f760d4787ac45aea7e4e905c445a3fd6323b3af4871fc1ed6d5f1662cab2")
f.close()


def return_private_key():
    """Reads the keys file and returns the private key"""
    file = open("keys.txt", "r")
    file_lines = file.readline()
    file.close()    
    return str.encode(file_lines)


