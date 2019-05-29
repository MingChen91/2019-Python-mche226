import urllib.request
import json
import base64
import storekey

def list_users(username,password):
    """ Lists current active users from login server"""
    url = "http://cs302.kiwi.land/api/list_users"

    headers = {
        'X-username': username,
        'X-apikey': "5LlakWWMaXOfByBdOzFy",
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

print(list_users("mche226","MingChen91_1636027"))