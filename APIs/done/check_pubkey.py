
import urllib.request
import json
import base64
import nacl.encoding
import nacl.signing
import storekey


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

url = "http://cs302.kiwi.land/api/check_pubkey?pubkey=" + verify_key_hex_str


try:
    # report
    req = urllib.request.Request(url, headers=headers)
    response = urllib.request.urlopen(req)
    data = response.read() # read the received bytes
    encoding = response.info().get_content_charset('utf-8') #load encoding if possible (default to utf-8)
    response.close()
    
except urllib.error.HTTPError as error:
    print(error.read())
    exit()

JSON_object = json.loads(data.decode(encoding))
print(JSON_object)
