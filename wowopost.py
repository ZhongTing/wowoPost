import os
import webapp2
import jinja2
import datetime
from google.appengine.ext import ndb

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__))
)

class Post(ndb.Model):
    message = ndb.StringProperty()
    to = ndb.StringProperty()
    time = ndb.DateTimeProperty()
    long_term_token = ndb.StringProperty()

class MainPage(webapp2.RequestHandler):

    def get(self):
        self.response.write('all post number = ' + str(Post.query().count()))
        posts = Post.query(Post.time < datetime.datetime.now()+datetime.timedelta(hours = 8))
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
        response = urllib2.urlopen("https://graph.facebook.com/oauth/access_token" +
                               "?" + urllib.urlencode(args)).read()
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
                    )
        key = post.put()
        self.response.write(key)
		
class AutoAddTestCase(webapp2.RequestHandler):
    def get(self):
        post = Post(
                    message='auto test msg',
                    to='123456789',
                    time=datetime.datetime.now(),
                    )
        key = post.put()
    
application = webapp2.WSGIApplication(
    [('/', MainPage),('/autoAdd',AutoAddTestCase)],
    debug=True
)