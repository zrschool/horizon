import webapp2
import logging
import jinja2
import os
from google.appengine.ext import ndb
from google.appengine.api import users
# from google.appengine.api import urlfetch
# import urllib
#import json


class Profile(ndb.Model):
    email = ndb.StringProperty()
    interests = ndb.KeyProperty(repeated = True)


class Interest(ndb.Model):
    interest_name = ndb.StringProperty()
    interest_description = ndb.StringProperty()


jinja_env = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.dirname(__file__))
)

creators = "Asia Collins, Bethelehem Engeda, Zachary Rideaux, and Isabella Siu"

class GetStartedPage(webapp2.RequestHandler):
    def get(self):
        name = self.request.get("name") or "World"

        template_vars = {
            "creators" : creators,
            "name" : name,
        }

        template = jinja_env.get_template("templates/get-started.html")
        self.response.write(template.render(template_vars))


class LoginPage(webapp2.RequestHandler):
    def get(self):
        current_user = users.get_current_user()
        email_address = current_user.email()
        current_profile = Profile.query().filter(Profile.email==email_address).get()

        if current_profile:
            print "No New Profile Added"
        else:
            Profile(
                email = current_user.email(),
                interests = [],
            ).put()
            print "New Profile Added"

        template = jinja_env.get_template("templates/login.html")
        self.response.write(template.render())
        self.redirect("/main")


class MainPage(webapp2.RequestHandler):
    def get(self):
        name = self.request.get("name") or "World"

        current_user = users.get_current_user()
        template_vars = {
            "creators" : creators,
            "name" : name,
            "current_user" : current_user,
        }

        template = jinja_env.get_template("templates/main.html")
        self.response.write(template.render(template_vars))


class UpdateDatabase(webapp2.RequestHandler):
    def get(self):
        template = jinja_env.get_template("templates/update-database.html")
        self.response.write(template.render())

        print("Hello")

<<<<<<< Updated upstream
    def post(self):
        current_user = users.get_current_user()
        # Create new interest based on input box
        interest = self.request.get("input-interest")
        new_interest = Interest(
            interest_name = interest,
            interest_description = "",
        )
        new_interest_key = new_interest.put()
        # Append new Interest to Profile Interests list
        current_profile = Profile.query().filter(Profile.email==current_user.email()).get()
        print current_profile
        print current_profile.interests
        print new_interest_key
        current_profile.interests.append(new_interest_key)
        current_profile.put()
        # Redirect to main
        self.redirect("/main")


=======
# class MainPage(webapp2.RequestHandler):
#     def get(self):

# 1. Set up my key and url
 #api_key = AIzaSyB6KsChF3TaIyOij8WIPlXNi_BY63DDYAU
 #base url = 'https://www.googleapis.com/books/v1/volumes?''
 # params {'q': 'Harry Potter',
 # 'api_key': api_key}
 # full_url = base_url + "?" + urllib.urlencode(params)
 #print full_url

# 2. Fetch url
# books_response = urlfetch.fetch(full_url).content

# 3. Get the JSON response and convert to a dictionary
#books_dictionary = json.loads(book_response)
# print 'books_dictionary', books_dictionary
#

#
#         template = jinja_env.get_template("templates/main.html")
#         self.response.write(template.render(template_vars))
>>>>>>> Stashed changes

app = webapp2.WSGIApplication([
    ("/", GetStartedPage),
    ("/main", MainPage),
    ("/update-database", UpdateDatabase),
    ("/login", LoginPage)
], debug=True)
