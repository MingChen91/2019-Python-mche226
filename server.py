import cherrypy
import urllib.request
import json
import base64
import server_api
import client_api
import helper_modules

redirect_html = '<!DOCTYPE html><html><head><meta http-equiv="Refresh" content="0; url=http://' + helper_modules.get_ip() + ':1234/"/></head></html>'

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
        username = cherrypy.session.get('username')
        if username is None:
            # redirect to index page
            return redirect_html
        else:
            return open("./static/main.html","r").read()

    # LOGGING IN AND OUT
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def signin(self):
        """ Checks incoming name and password, gives response if ok not not \n
            If ok, store usename and apikey in session """
        incoming_data =cherrypy.request.json
        success = authorise_user_login(incoming_data['username'],incoming_data['password'])
        if success != False:
            cherrypy.session['username'] = incoming_data['username']
            cherrypy.session['api_key'] = success['api_key']
            cherrypy.log("Successful Authentication")
            return json.dumps({"response":"ok"})
        else:
            return json.dumps({"response":" Couldn't authenticate"})


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
    """checks using ping against login server to see if credentials are valid"""
    response = server_api.load_api_key(username,password)
    print(response)
    if response == False:
        return False
    else:
        return response


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


