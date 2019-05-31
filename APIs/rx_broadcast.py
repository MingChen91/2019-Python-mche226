import urllib.request
import json
import base64
import nacl.encoding
import nacl.signing
import storekey
import time


url = "http://cs302.kiwi.land/api/rx_broadcast"
private_key_hex = storekey.return_private_key()

#create HTTP BASIC authorization header
username = "Mche226"
password = "MingChen91_1636027"

credentials = ('%s:%s' % (username, password))
b64_credentials = base64.b64encode(credentials.encode('ascii'))
headers = {
    'Authorization': 'Basic %s' % b64_credentials.decode('ascii'),
    'Content-Type' : 'application/json; charset=utf-8',
}


# Generate a new random signing key / private key generation and converting to json format
signing_key = nacl.signing.SigningKey(private_key_hex, encoder=nacl.encoding.HexEncoder)

#public pair / converting to json
verify_key = signing_key.verify_key
verify_key_hex_str =  verify_key.encode(nacl.encoding.HexEncoder).decode('utf-8')
login_server_record = "mche226,b9eba910b59549774d55d3ce49a7b4d46ab5e225cdcf2ac388cf356b5928b6bc,1558396877.296010,8369b9da8c9c6e1517ac70756d4d13ce406d8ff9f6c4e4bbce40436ca4e1d1f938f10b8289d9b3f65b6dbf5d0a3df8c4343f50f2db5dcfff142dbf37c8f3db00"

time_creation = str(time.time())
message = "jacob how do you bypass the time stamp"
#sign the message, which is the public + name
message_bytes = bytes(login_server_record+message+time_creation, encoding='utf-8')

signed =signing_key.sign(message_bytes, encoder=nacl.encoding.HexEncoder)
signature_hex_str = signed.signature.decode('utf-8')


payload = {
    "loginserver_record" : login_server_record,
    "message" : message,
    "sender_created_at" : time_creation,
    "signature" : signature_hex_str
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
    
except urllib.error.HTTPError as error:
    print(error.read())
    exit()

JSON_object = json.loads(data.decode(encoding))
print(JSON_object)
