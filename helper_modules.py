import socket
import urllib.request
import json
from time import ctime
##
## USED AS CONFIG
##
def get_port():
    """ Set your external port here"""
    return 80

def get_internal_port():
    """ Set your internal port"""
    return 10069

def get_connect_location():
    """ Set your connection address here, 0 for uni ethernet, 1 for uni wireless, 2 for rest of the world"""
    return 1
##    
## USED AS CONFIG
##

def get_external_ip():
    """ Returns public IP by getting it from ident.me """
    external_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')
    return external_ip


def get_ip():
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

        response = urllib.request.urlopen(req,timeout=5)
        data = response.read() # read the received bytes
        encoding = response.info().get_content_charset('utf-8') #load encoding if possible (default to utf-8)
        response.close()
        return json.loads(data.decode(encoding))
    except urllib.error.HTTPError as error:
        print(error.read())
        return 0
    except urllib.error.URLError as error:
        if isinstance(error.reason,socket.timeout):
            print(error.reason)
            return 0
    except Exception as error:
        print (error)
        return 0 


def convert_time(time_str):
    """converts time to local time"""
    try:
        if (type(time_str) == float):
            local_time = ctime(time_str)
        else :
            local_time = ctime(float(time_str))
        return(local_time)
    except:
        return (time_str)


