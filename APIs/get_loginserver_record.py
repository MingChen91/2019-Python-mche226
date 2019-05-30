import urllib.request
import json
import base64


def get_loginserver_record(username,password):
    """ Use this API to load your current loginserver_record for use in creating
    point-to-point messages. Change it by creating new pubkeys with /api/add_pubkey and/or by
    changing the current pubkey in /api/report."""
    url = "http://cs302.kiwi.land/api/get_loginserver_record"

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
    return(response_dict["loginserver_record"])

# print(get_loginserver_record("mche226","MingChen91_1636027"))
