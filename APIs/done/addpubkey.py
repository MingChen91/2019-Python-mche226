import urllib.request
import json
import nacl.encoding
import nacl.signing
import storekey
from api_key import read_apikey_txt


def add_pubkey(username):
    """Associate a public key with your account. This key pair is used for signing
    returns the response as a dict"""

    url = "http://cs302.kiwi.land/api/add_pubkey"
    private_key_hex_bytes = storekey.return_private_key()
    api_key = read_apikey_txt()
    headers = {
        'X-username': username,
        'X-apikey': api_key,
        'Content-Type' : 'application/json; charset=utf-8',
    }

    # Uses the stored signing key hex bytes to reconstruct the key pair. 
    signing_key = nacl.signing.SigningKey(private_key_hex_bytes, encoder=nacl.encoding.HexEncoder)
    # Getting the public key
    verify_key = signing_key.verify_key
    # Convert to bytes, then decode to string
    verify_key_hex_str = verify_key.encode(nacl.encoding.HexEncoder).decode('utf-8')
    # Message is verify key + username
    message_bytes = bytes(verify_key_hex_str + username, encoding='utf-8')
    # Sign the message, which is the public + name
    signed = signing_key.sign(message_bytes, encoder=nacl.encoding.HexEncoder)
    signature_hex_str = signed.signature.decode('utf-8')

    payload = {
        "pubkey": verify_key_hex_str,
        "username": username,
        "signature": signature_hex_str,
    }

    payload_str = json.dumps(payload)
    payload_data = payload_str.encode('utf-8')

    try:
        # report
        req = urllib.request.Request(url, data=payload_data, headers=headers)
        response = urllib.request.urlopen(req)
        data = response.read()  # read the received bytes
        # load encoding if possible (default to utf-8)
        encoding = response.info().get_content_charset('utf-8')
        response.close()

    except urllib.error.HTTPError as error:
        print(error.read())
        exit()

    response_dict = json.loads(data.decode(encoding))
    return response_dict
