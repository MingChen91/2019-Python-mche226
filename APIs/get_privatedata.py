import urllib.request
import json
import base64
import storekey
from api_key import read_apikey_txt
def get_privatedata(username,password):
    """ Use this API to load the saved symmetrically encrypted private data for a user. """
    url = "http://cs302.kiwi.land/api/get_privatedata"
    api_key = read_apikey_txt()

    headers = {
        'X-username': username,
        'X-apikey': api_key,
        'Content-Type' : 'application/json; charset=utf-8',
    }

    try:
        req = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(req)
        data = response.read() # read the received bytes
        encoding = response.info().get_content_charset('utf-8') #load encoding if possible (default to utf-8)
        response.close()
    except urllib.error.HTTPError as error:
        print(error.read())
        exit()

    response_dict = json.loads(data.decode(encoding))
    return(response_dict)

print(get_privatedata("mche226","MingChen91_1636027"))