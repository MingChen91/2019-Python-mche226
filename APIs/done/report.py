import urllib.request
import json
import nacl.encoding
import nacl.signing
import key_manager
 
def report(username,status = 'online'):
    """ Informs login server about connection information. 
    Call this at least once every 5 minutes and at most once
    every 30 seconds. Optional status 'online, 'away', 'busy', 'offline'"""

    url = "http://cs302.kiwi.land/api/report"

    headers = {
        'X-username': username,
        'X-apikey': "BZ6SSVojyjeoKh3E6sdr",
        'Content-Type' : 'application/json; charset=utf-8',
    }

    private_key_hex = key_manager.return_private_key()
    
    # Generate a new random signing key / private key generation and converting to json format
    signing_key = nacl.signing.SigningKey(private_key_hex, encoder=nacl.encoding.HexEncoder)
    #public pair / converting to json
    verify_key = signing_key.verify_key
    verify_key_hex_str =  verify_key.encode(nacl.encoding.HexEncoder).decode('utf-8')

    payload = {
        "connection_location": "2",
        "connection_address": "172.23.68.84",
        "incoming_pubkey" : verify_key_hex_str,
        "status" : status
    }

    payload_str = json.dumps(payload)
    payload_data = payload_str.encode('utf-8')

    try:
        req = urllib.request.Request(url, data=payload_data, headers=headers)
        response = urllib.request.urlopen(req)
        data = response.read() # read the received bytes
        encoding = response.info().get_content_charset('utf-8') #load encoding if possible (default to utf-8)
        response.close()
    except urllib.error.HTTPError as error:
        print(error.read())
        exit()

    response_dict = json.loads(data.decode(encoding))
    return(response_dict)

print(report("mche226","away"))