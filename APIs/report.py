import urllib.request
import json
import base64
import nacl.encoding
import nacl.signing

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


private_key_hex = b'ecd0f760d4787ac45aea7e4e905c445a3fd6323b3af4871fc1ed6d5f1662cab2'
# Generate a new random signing key / private key generation and converting to json format
signing_key = nacl.signing.SigningKey(private_key_hex, encoder=nacl.encoding.HexEncoder)

#public pair / converting to json
verify_key = signing_key.verify_key
verify_key_hex_str =  verify_key.encode(nacl.encoding.HexEncoder).decode('utf-8')



payload = {#     STUDENT TO COMPLETE THIS...
    "connection_location": "2",
    "connection_address": "127.0.0.1:8000",
    "incoming_pubkey" : verify_key_hex_str
}


payload_str = json.dumps(payload)
payload_data = payload_str.encode('utf-8')

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
