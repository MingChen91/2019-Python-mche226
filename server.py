import cherrypy
import urllib.request
import json
import base64
import server_api
import client_api
import database
import helper_modules
from cgi import escape
from time import time
from jinja2 import Environment, FileSystemLoader

# Jinja and pagesenviroment
env = Environment(loader = FileSystemLoader('static'))
index_page= env.get_template('index.html')
main_page= env.get_template('main.html')


class MainApp(object):
    """ Colletion of Main functions for Javascript to call"""
    
    # CherryPy Configuration
    _cp_config = {
                    'tools.encode.on': True, 
                    'tools.encode.encoding': 'utf-8',
                    'tools.sessions.on': 'True',
                 }

    
    # If they try somewhere we don't know, catch it here and send them to the right place.
    @cherrypy.expose
    def default(self, *args, **kwargs):
        """ Redirect to index if they go to the wrong place"""
        return index_page.render()



    # PAGES (which return HTML that can be viewed in browser)
    @cherrypy.expose
    def index(self):
        """serves index.html"""
        return index_page.render()


    @cherrypy.expose
    def main(self):
        """ Serves the main html"""
        username = cherrypy.session.get('username')
        if username is None:
            # redirect to index page if no active session
            raise cherrypy.HTTPRedirect('/index')
        else:

            return main_page.render(username = username.capitalize())


    ##
    # private data
    ##
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def create_new_private_data(self):
        """ Creates a new set of private keys and private data for them"""
        incoming = cherrypy.request.json
        username = incoming['username']
        password = incoming['password']
        priv_password = incoming['priv_password']
        # new private key hex string
        new_priv_hex_str = server_api.new_key()

        api_key_dict = server_api.load_api_key(username,password)
        if api_key_dict == None:
            return json.dumps({'response':'error getting api key'})

        """ Add for them """
        loaded_new_pubkey = server_api.add_pubkey(username,api_key_dict['api_key'],new_priv_hex_str)
        if loaded_new_pubkey ==None:
             return json.dumps({'response':'error adding new pubkey'})

        private_data = [[new_priv_hex_str],[""],[""],[""],[""],[""]]
        server_api.add_privatedata(username,api_key_dict['api_key'],priv_password,private_data,new_priv_hex_str)
        
        return json.dumps ({'response':'ok'})
        


    ##
    # LOGGING IN AND OUT
    ##
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def signin(self):
        """ Checks incoming name and password, gives response if ok \n
            If ok, store usename and apikey in session. \n
            Then checks tries to get private data, can get, store privkey in session.\n
            If not add new pubkey and store new private key in session. 
            """
        # Incoming request
        incoming_data =cherrypy.request.json
        success = authorise_user_login(incoming_data['username'],incoming_data['password'])
        
        # if successfully authorised load apikey and username in 
        if success != False:
            # tries to load their private data. 
            private_data = load_private_data(incoming_data['username'],success['api_key'],incoming_data['priv_password'])
            
            if private_data == True:
                cherrypy.session['username'] = incoming_data['username']
                cherrypy.session['api_key'] = success['api_key']
                cherrypy.log("Authenticated and loaded private data")
                return json.dumps({"response":"ok"})
            else:
                cherrypy.log("Authenticated but couldn't get private data")
                return json.dumps({"response":"Can't load private data"})
        else:
            cherrypy.log("Unsuccessful Authentication")
            return json.dumps({"response":" Can't authenticate"})


    @cherrypy.expose
    def signout(self):
        """Logs the current user out, expires their session"""
        username = cherrypy.session.get('username')
        if username is None:
            cherrypy.log("Already logged out")
        else:
            server_api.report(cherrypy.session.get('username'),cherrypy.session.get('api_key'),cherrypy.session.get('privkeys'),'offline')
            cherrypy.lib.sessions.expire()
            cherrypy.log("Logged out of session")
            
      
    ##
    # Listing users
    ##
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def list_users(self):
        """ Calls refreshes all the status of other users"""
        # Calls list users and adds their data to the database
        database.update_accounts_data(cherrypy.session.get('username'),cherrypy.session.get('api_key'))
        # Returns the ones with active connections. 
        response = database.get_all_users()
        return json.dumps(response)


    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def report(self) :
        # Reports status to server
        incoming_data =cherrypy.request.json
        status = incoming_data['status']
        # tries to report
        success = server_api.report(cherrypy.session.get('username'),cherrypy.session.get('api_key'),cherrypy.session.get('privkeys'),status)
        if success == None:
            return json.dumps({"response":"Can't report"})
        else:
            return json.dumps({"response":"ok"})
        

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def broadcast(self):
        """ Call this API to send a broadcast to all the users that are reported as online"""
        incoming_data = cherrypy.request.json
        message = incoming_data['message']
        client_api.broadcast_to_all(cherrypy.session.get('username'),cherrypy.session.get('api_key'), cherrypy.session.get('loginserver_record'),cherrypy.session.get('privkeys'),message)
        return json.dumps({"response" : "ok"})

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def private_message(self):
        """ Call this API to send a broadcast to all the users that are reported as online"""
        incoming_data = cherrypy.request.json
        message = incoming_data['message']
        target_username = incoming_data['target_username']

        client_api.private_message_all(cherrypy.session.get('username'),cherrypy.session.get('api_key'),target_username,cherrypy.session.get('loginserver_record'),cherrypy.session.get('privkeys'),message)
        return json.dumps({"response" : "ok"})   

    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_broadcast(self):
        """ Fetches all the broadcast message from database"""
        return json.dumps(database.get_broadcast_message())

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def get_private_message(self):
        """ Fetches all messages sent and received to a target user"""
        incoming_data = cherrypy.request.json
        target_username  =incoming_data['target_username']

        private_messages = database.get_private_message(cherrypy.session.get('username'),target_username,cherrypy.session.get('privkeys'))
        return json.dumps(private_messages)


###
# Interal Functions
###

#signing in ones
def authorise_user_login(username,password):
    """ Checks using ping against login server to see if credentials are valid\n
        Returns the APIkey if is ok """

    response = server_api.load_api_key(username,password)
    
    if (response == False):
        return False
    else:
        cherrypy.session['loginserver_record'] = server_api.get_loginserver_record(username,response['api_key'])
        if cherrypy.session.get('loginserver_record') != None:
            return response
        else:
            return False

def load_private_data(username,api_key,priv_password):
    """ Loads private data for user. If can't load private data for any reason create new private data for them"""
    # attemps to load private data
    private_data = server_api.get_privatedata(username,api_key,priv_password)
    if private_data == None:
        # Return false and tell them couldn't load private data properly
        return False
    else: 
        # loads all the data into sessions
        cherrypy.session['privkeys'] = private_data['prikeys'][0]
        return True



########################
## External API calls ##
########################
class ApiCollection(object):
    """ Collection of API endpoint"""
    # CherryPy Configuration
    _cp_config = {
                    'tools.encode.on': True, 
                    'tools.encode.encoding': 'utf-8',
                    'tools.sessions.on': 'True',
                 }
    
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def rx_broadcast(self):
        """ Endpoint for other users to send broadcasts to this server"""
        # incoming_data = json.loads(cherrypy.request.body.read().decode('utf-8'))
        incoming_data =cherrypy.request.json
        # Preventing HTML injections
        loginserver_record = escape(incoming_data['loginserver_record'], quote=True)
        message = escape(incoming_data['message'], quote=True)
        sender_created_at = escape(incoming_data['sender_created_at'], quote=True)
        signature = escape(incoming_data['signature'], quote=True)

        database.add_broadcast_message(loginserver_record,message,sender_created_at,signature)
        response= {
            "response": "ok"
        }
        json_data_str = json.dumps(response)
        return json_data_str

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def rx_privatemessage(self):
        """ Endpoint for other users to send private messages to this server"""
        incoming_data = cherrypy.request.json
        loginserver_record = escape(incoming_data['loginserver_record'],quote=True)
        target_pubkey = escape(incoming_data['target_pubkey'],quote=True)
        target_username = escape(incoming_data['target_username'],quote=True)
        encrypted_message = escape(incoming_data['encrypted_message'],quote=True)
        sender_created_at = escape(incoming_data['sender_created_at'],quote=True)
        signature = escape(incoming_data['signature'],quote=True)

        database.add_private_message(loginserver_record,target_pubkey,target_username,encrypted_message,sender_created_at,signature,'')

        response= {
            "response": "ok"
        }
        
        return json.dumps(response)

    
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def ping_check(self):
        """ Call this API to establish if a client is actually online and can conenct to them correctly"""
        current_time = str(time())
        response = {
            'response':'ok',
            'my_time':current_time
        }
        return json.dumps(response)
        
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def ping_check(self):
        """ redirects to ping check"""
        raise cherrypy.HTTPRedirect('/api/ping_check')

#####
## External Functions
#####


