import cherrypy
import urllib.request
import json
import base64
import server_api
import database
import helper_modules
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
        """The default page, given when we don't recognise where the request is for."""
        cherrypy.response.status = 404
        return "I DONT THINK YOU'RE SUPPOSED TO BE HERE AYE."


    # PAGES (which return HTML that can be viewed in browser)
    @cherrypy.expose
    def index(self):
        """serves index.html
        TODO error catching"""
        return index_page.render()


    @cherrypy.expose
    def main(self):
        """ Serves the main html"""
        username = cherrypy.session.get('username')
        if username is None:
            # redirect to index page
            raise cherrypy.HTTPRedirect('/index')
        else:
            return main_page.render()



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
            # pass
        else:
            cherrypy.lib.sessions.expire()
            cherrypy.log("Logged out of session")
      

    ##
    # Listing users
    ##
    @cherrypy.expose
    def list_users(self):
        """ Pulls list of users from Hammonds server, updates the database, then returns the data in a JSON"""
        cherrypy.log("LIST USERS CALLED \n")
        # server_api.list_users(cherrypy.session.get('username'), cherrypy.session.get('api_key'))


    @cherrypy.expose
    def broadcast(self, message=None):
        """Check their name and password and send them either to the main page, or back to the main login screen."""
        error = client_api.broadcast(cherrypy.session.get('username'),message)
        if error == 0:
            raise cherrypy.HTTPRedirect('/')
        else:
            raise cherrypy.HTTPRedirect('/login?bad_attempt=1')


###
# Interal Functions
###
#signing in ones
def authorise_user_login(username,password):
    """ Checks using ping against login server to see if credentials are valid\n
        Returns the APIkey if is ok """

    response = server_api.load_api_key(username,password)
    if response == False:
        return False
    else:
        return response

def load_private_data(username,api_key,priv_password):
    """ Loads private data for user. If can't load private data for any reason create new private data for them"""
    # attemps to load private data
    private_data = server_api.get_privatedata(username,api_key,priv_password)
    if private_data == None:
        # Return false and tell them couldn't load private data properly
        return False
    else: 
        # loads all the data into sessions
        cherrypy.session['privkeys'] = private_data['prikeys']
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
        print(incoming_data)
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
        incoming_data =cherrypy.request.json
        print(incoming_data)
        response= {
            "response": "ok"
        }
        json_data_str = json.dumps(response)
        return json_data_str
        

#####
## External Functions
#####


