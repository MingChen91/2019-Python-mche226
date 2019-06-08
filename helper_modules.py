import socket
import urllib.request
import json

def get_ip():
    """ Returns public IP by getting it from ident.me """
    # if identme is down, use the commented code. which only gets local IP. sometimes different to public ip
    # external_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')
    # return external_ip

    """ Returns the local IP"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    # print(IP)
    return IP


def send_data(url, headers = None, data = None):
    """ Module used to communicate with other APIs. """
    try:
        if (headers == None):
            req = urllib.request.Request(url)
        elif (data == None):
            req = urllib.request.Request(url,headers=headers)   
        else:
            req = urllib.request.Request(url, data = data, headers=headers)

        response = urllib.request.urlopen(req)
        data = response.read() # read the received bytes
        encoding = response.info().get_content_charset('utf-8') #load encoding if possible (default to utf-8)
        response.close()
        return json.loads(data.decode(encoding))
        
    except urllib.error.HTTPError as error:
        print(error.read())
        return error
    
    except Exception as error:
        print (error)
        return error 