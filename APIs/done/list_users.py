import urllib.request
import json
import base64
from api_key import read_apikey_txt

def list_users(username,password):
    """ Lists current active users from login server"""
    url = "http://cs302.kiwi.land/api/list_users"
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

