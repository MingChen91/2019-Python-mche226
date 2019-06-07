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