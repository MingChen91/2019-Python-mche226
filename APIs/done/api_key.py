import urllib.request
import json
import base64
import storekey


def load_api_key(username,password):
    """ Retrives an API key, Makesure to store this key. New key to be generate each session """
    url = "http://cs302.kiwi.land/api/load_new_apikey"

    credentials = ('%s:%s' % (username, password))
    b64_credentials = base64.b64encode(credentials.encode('ascii'))
    headers = {
        'Authorization': 'Basic %s' % b64_credentials.decode('ascii'),
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
    output_apikey_txt(response_dict['api_key'])
    return(response_dict)


def output_apikey_txt(apikey):
    file = open("api_keys.txt", "w+")
    file.write(apikey)
    file.close()    

def read_apikey_txt():
    file = open("api_keys.txt","r")
    file_lines = file.readline()
    file.close()    
    return (file_lines)

# load_api_key("Mche226","MingChen91_1636027")


# 5LlakWWMaXOfByBdOzFy