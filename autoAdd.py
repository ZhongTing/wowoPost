import webapp2
import datetime
import wowopost
class AutoAddTestCase(webapp2.RequestHandler):
    def get(self):
        post = wowopost.Post(
                    message='auto test msg',
                    to='123456789',
                    time=datetime.datetime.now(),
                    )
        key = post.put()

        
app = webapp2.WSGIApplication([
    ('/autoAdd',AutoAddTestCase),
], debug=True)