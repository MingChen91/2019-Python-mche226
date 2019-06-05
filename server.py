import cherrypy
import urllib.request
import json
import base64
import server_api
import client_api

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
        return open("./static/index.html","r").read()

    @cherrypy.expose
    def main(self):
        """serves the main html"""
        return open("./static/main.html","r").read()

    # LOGGING IN AND OUT
    @cherrypy.expose
    def signin(self, username=None, password=None):
        """Check their name and password and send them either to the main page, or back to the main login screen."""
        
        # if error == 0:
        #     cherrypy.session['username'] = username
        #     cherrypy.log("Successful Authentication")

        response = json.dumps({"response":"sok"})
        return response


    @cherrypy.expose
    def signout(self):
        """Logs the current user out, expires their session"""
        username = cherrypy.session.get('username')
        if username is None:
            pass
        else:
            cherrypy.lib.sessions.expire()
        raise cherrypy.HTTPRedirect('/')

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
def authorise_user_login(username,password):
    """checks using ping against login server to see if credentials are valid"""
    response = server_api.load_api_key(username,password)
    if response == True:
        return 0
    else:
        return 1


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
        # incoming_data = json.loads(cherrypy.request.body.read().decode('utf-8'))
        incoming_data =cherrypy.request.json
        print(incoming_data)
        
        response= {
            "response": "ok"
        }
        json_data_str = json.dumps(response)
        return json_data_str

    def test(self):
        print("hello")

    #####
    ## External Functions
    #####


