import cherrypy
import urllib.request
import json
import base64
import server_api
import client_api

startHTML = """ <html>
                    <head>
                        <title>CS302 example</title>
                        <link rel='stylesheet' href='/static/example.css' />
                    </head>
                    <body>"""


class MainApp(object):

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
        Page = startHTML + "I don't know where you're trying to go, so have a 404 Error."
        cherrypy.response.status = 404
        return Page


    # PAGES (which return HTML that can be viewed in browser)
    @cherrypy.expose
    def index(self):
        Page = startHTML + "Welcome! This is a test website for COMPSYS302!<br/>"

        try:
            Page += "Hello " + cherrypy.session['username'] + "!<br/>"
            Page += "F is for friends to do stuff together, U is for U n ME, N is for NEwhere! <a href='/signout'>Sign out</a>"

            Page += '<form action="/broadcast" method="post" enctype="multipart/form-data">'
            Page += 'Message: <input type="text" name="message"/><br/>'
            Page += '<input type="submit" value="send to hammond!"/></form>'

        except KeyError: #There is no username
            Page += "Click here to <a href='login'>login</a>."
        return Page


    @cherrypy.expose
    def login(self, bad_attempt = 0):
        Page = startHTML 
        if bad_attempt != 0:
            Page += "<font color='red'>Invalid username/password!</font>"

        Page += '<form action="/signin" method="post" enctype="multipart/form-data">'
        Page += 'Username: <input type="text" name="username"/><br/>'
        Page += 'Password: <input type="text" name="password"/>'
        Page += '<input type="submit" value="Login"/></form>'
        return Page

    # LOGGING IN AND OUT
    @cherrypy.expose
    def signin(self, username=None, password=None):
        """Check their name and password and send them either to the main page, or back to the main login screen."""
        error = authorise_user_login(username, password)
        if error == 0:
            cherrypy.session['username'] = username
            cherrypy.log("Successful Authentication")
            raise cherrypy.HTTPRedirect('/')
        else:
            cherrypy.log("Authentication error.")
            raise cherrypy.HTTPRedirect('/login?bad_attempt=1')


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

    def check_existing_key(self,username):
        """ Checks if there's an existing key pair for this user, returns True or False"""
        # Select the prikeys 
        response = server_api.get_privatedata(username)
        # privatedata_dict = json.loads(response['privatedata'])
        print(response['private'])
        # print (type(privatedata_dict['prikeys']))
        # print (response['privatedata'])
        # print (type(privatedata_dict))



# testing functions as i go along
test = ApiCollection()
test.check_existing_key("mche226")

###
# Functions only after here
###
def authorise_user_login(username,password):
    """checks using ping against login server to see if credentials are valid"""
    response = server_api.load_api_key(username,password)
    if response == True:
        return 0
    else:
        return 1


