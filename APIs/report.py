import urllib.request
import json
import base64

url = "http://cs302.kiwi.land/api/report"

#STUDENT TO UPDATE THESE...
username = "Mche226"
password = "MingChen91_1636027"

#create HTTP BASIC authorization header
credentials = ('%s:%s' % (username, password))
b64_credentials = base64.b64encode(credentials.encode('ascii'))
headers = {
    'Authorization': 'Basic %s' % b64_credentials.decode('ascii'),
    'Content-Type' : 'application/json; charset=utf-8',
}

payload = {#     STUDENT TO COMPLETE THIS...
    "connection_location": "2",
    "connection_address": "127.0.0.1:8000"
}


payload_str = json.dumps(payload)
payload_data = payload_str.encode('utf-8')

#STUDENT TO COMPLETE:
#1. convert the payload into json representation, 
#2. ensure the payload is in bytes, not a string
#3. pass the payload bytes into this function


try:
    # report
    req = urllib.request.Request(url, data=payload_data, headers=headers)
    response = urllib.request.urlopen(req)
    data = response.read() # read the received bytes
    encoding = response.info().get_content_charset('utf-8') #load encoding if possible (default to utf-8)
    response.close()


    # list users
    req2 = urllib.request.Request("http://cs302.kiwi.land/api/list_users", headers=headers)
    response2 = urllib.request.urlopen(req2)
    data2 = response2.read() # read the received bytes
    encoding2 = response2.info().get_content_charset('utf-8') #load encoding if possible (default to utf-8)
    response2.close()


except urllib.error.HTTPError as error:
    print(error.read())
    exit()

JSON_object = json.loads(data.decode(encoding))
print(JSON_object)

JSON_object = json.loads(data2.decode(encoding2))
print(JSON_object)
