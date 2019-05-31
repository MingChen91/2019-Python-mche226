import urllib.request
import json
import base64
import storekey

def loginserver_pubkey():
    """ Return the public key of the login server, which may be used to validate
        loginserver_records in broadcasts / private messages """
    url = "http://cs302.kiwi.land/api/loginserver_pubkey"

    try:
        req = urllib.request.Request(url)
        response = urllib.request.urlopen(req)
        data = response.read() # read the received bytes
        encoding = response.info().get_content_charset('utf-8') #load encoding if possible (default to utf-8)
        response.close()
    except urllib.error.HTTPError as error:
        print(error.read())
        exit()

    response_dict = json.loads(data.decode(encoding))
    return(response_dict)

print(loginserver_pubkey())