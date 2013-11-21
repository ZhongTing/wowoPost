import os
import webapp2
import jinja2
import datetime
from google.appengine.ext import ndb

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class Post(ndb.Model):
    message = ndb.StringProperty()
    to = ndb.StringProperty()
    time = ndb.DateTimeProperty()

class MainPage(webapp2.RequestHandler):

    def get(self):
        self.response.write('all post number = ' + str(Post.query().count()))
        posts = Post.query(Post.time < datetime.datetime.now())
        for p in posts:
            self.response.write('<br/>' + str(p) + '<br/>')
            #p.key.delete()
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render())
    def post(self):
        t=self.request.get('time')
        post = Post(
                    message=self.request.get('message'),
                    to=self.request.get('to'),
                    time=datetime.datetime.now(),
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
    

application = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)