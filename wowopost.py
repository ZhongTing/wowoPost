import os
import re
import webapp2
import jinja2
import datetime
import urllib
import urllib2
import facebook

from google.appengine.ext import db
from google.appengine.ext import ndb
from webapp2_extras import sessions

FACEBOOK_APP_ID = "351096461701940"
FACEBOOK_APP_SECRET = "0939c0395ed7e7c9a2eff9ea160e794b"

config = {}
config['webapp2_extras.sessions'] = dict(secret_key='')

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__))
)

class User(db.Model):
    id = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    name = db.StringProperty(required=True)
    profile_url = db.StringProperty(required=True)
    access_token = db.StringProperty(required=True)

class Post(ndb.Model):
    sender = ndb.StringProperty()
    message = ndb.StringProperty()
    to = ndb.StringProperty()
    time = ndb.DateTimeProperty()
    long_term_token = ndb.StringProperty()
    
class BaseHandler(webapp2.RequestHandler):
    """Provides access to the active Facebook user in self.current_user

    The property is lazy-loaded on first access, using the cookie saved
    by the Facebook JavaScript SDK to determine the user ID of the active
    user. See http://developers.facebook.com/docs/authentication/ for
    more information.
    """
    @property
    def current_user(self):
        if self.session.get("user"):
            # User is logged in
            return self.session.get("user")
        else:
            # Either used just logged in or just saw the first page
            # We'll see here
            cookie = facebook.get_user_from_cookie(self.request.cookies,
                                                   FACEBOOK_APP_ID,
                                                   FACEBOOK_APP_SECRET)
            if cookie:
                # Okay so user logged in.
                # Now, check to see if existing user
                user = User.get_by_key_name(cookie["uid"])
                if not user:
                    # Not an existing user so get user info
                    graph = facebook.GraphAPI(cookie["access_token"])
                    profile = graph.get_object("me")
                    user = User(
                        key_name=str(profile["id"]),
                        id=str(profile["id"]),
                        name=profile["name"],
                        profile_url=profile["link"],
                        access_token=cookie["access_token"]
                    )
                    user.put()
                elif user.access_token != cookie["access_token"]:
                    user.access_token = cookie["access_token"]
                    user.put()
                # User is now logged in
                self.session["user"] = dict(
                    name=user.name,
                    profile_url=user.profile_url,
                    id=user.id,
                    access_token=user.access_token
                )
                return self.session.get("user")
        return None

    def dispatch(self):
        """
        This snippet of code is taken from the webapp2 framework documentation.
        See more at
        http://webapp-improved.appspot.com/api/webapp2_extras/sessions.html

        """
        self.session_store = sessions.get_store(request=self.request)
        try:
            webapp2.RequestHandler.dispatch(self)
        finally:
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        """
        This snippet of code is taken from the webapp2 framework documentation.
        See more at
        http://webapp-improved.appspot.com/api/webapp2_extras/sessions.html

        """
        return self.session_store.get_session()
    
class MainPage(BaseHandler):

    def get(self):
        self.response.write('all post number = ' + str(Post.query().count()))
        posts = Post.query()
        for p in posts:
			self.response.write('<br/>' + str(p) + '<br/>')
			#p.key.delete()
        template = jinja_environment.get_template('/index.html')
        self.response.write(template.render())
	
    def post(self):
        args = {
            "grant_type": 'fb_exchange_token',
            "client_id": FACEBOOK_APP_ID,
            "client_secret": FACEBOOK_APP_SECRET,
            "fb_exchange_token": self.current_user['access_token'],
        }

        response = urllib2.urlopen("https://graph.facebook.com/oauth/access_token" + "?" + urllib.urlencode(args)).read()
        token = re.match( r'access_token=(.*)&.*', response).group(1)
        year = int(self.request.get('year'))
        month = int(self.request.get('month'))
        day = int(self.request.get('day'))
        hour = int(self.request.get('hour'))
        min = int(self.request.get('min'))
        
        post = Post(
                    message=self.request.get('message'),
                    to=self.request.get('to'),
                    time=datetime.datetime(year,month,day,hour,min),
                    long_term_token = token,
                    sender = self.current_user['id']
                    )
        key = post.put()
        self.response.write(token)
        self.response.write('<br/>')
        self.response.write(key)
        
class PostConsumer(webapp2.RequestHandler):
    def get(self):
        posts = Post.query(Post.time < datetime.datetime.now()+datetime.timedelta(hours = 8))
        for p in posts:
            graph = facebook.GraphAPI(p.long_term_token)
            attachment = {}
            attachment["to"] = p.to
            attachment["place"] = 108479922509500
            attachment["tags"] = p.to
            post_object_id = graph.put_wall_post(p.message, attachment)
            self.response.write(post_object_id)
            self.response.write('<br/>')
            p.key.delete()

class TaskViewer(BaseHandler):
    def get(self):
        posts = Post.query(Post.sender == self.current_user['id'])
        for p in posts:
            self.response.write('<br/>' + str(p) + '<br/>')
            
    
application = webapp2.WSGIApplication(
    [('/', MainPage),('/list', TaskViewer),('/ConsumePost',PostConsumer)],
    debug=True,
    config=config
)
