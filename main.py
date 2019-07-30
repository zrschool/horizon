import webapp2
import logging
import jinja2
import os
from google.appengine.ext import ndb
from google.appengine.api import users



class Interest(ndb.Model):
    interest_name = ndb.StringProperty()
    interest_description = ndb.StringProperty()


class Profile(ndb.Model):
    email = ndb.StringProperty()
    interests = ndb.KeyProperty(kind = Interest, repeated = True)

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



class MainPage(webapp2.RequestHandler):
    def get(self):
        name = self.request.get("name") or "World"

        profile_key = ndb.Key(urlsafe=self.request.get("key"))
        current_profile = profile_key.get()

        current_user = users.get_current_user()
        # current_profile
        # Profile.query().filter(Profile.email==current_user.email()).get()


        template_vars = {
            "creators" : creators,
            "name" : name,
            "current_user" : current_user,
            "current_profile" : current_profile,

        }

        # print "Current Profile: "
        # print current_profile
        # print "Current User: "
        # print current_user


        template = jinja_env.get_template("templates/main.html")
        self.response.write(template.render(template_vars))

class LoginPage(webapp2.RequestHandler):
    def get(self):
        current_user = users.get_current_user()
        email_address = current_user.email()
        current_profile = Profile.query().filter(Profile.email==email_address).get()
        current_profile_key = ""

        if current_profile:
            current_profile_key = current_profile.key
            print "No New Profile Added"
        else:
            current_profile = Profile(
                email = current_user.email(),
                interests = [],
            )
            current_profile_key = current_profile.put()
            print "New Profile Added"

        self.redirect("/main?key=" + current_profile_key.urlsafe())

class UpdateDatabase(webapp2.RequestHandler):
    def get(self):
        template = jinja_env.get_template("templates/update-database.html")
        self.response.write(template.render())


    def post(self):
        current_user = users.get_current_user()
        # Create new interest based on input box
        input_interest = self.request.get("input-interest")
        new_interest = Interest(
            interest_name = input_interest,
            interest_description = "",
        )
        new_interest_key = new_interest.put()
        # Append new Interest to Profile Interests list
        current_profile = Profile.query().filter(Profile.email==current_user.email()).get()

        current_profile.interests.append(new_interest_key)
        current_profile_key = current_profile.put()
        # Redirect to main
        self.redirect("/main?key=" + current_profile_key.urlsafe())



app = webapp2.WSGIApplication([
    ("/", GetStartedPage),
    ("/main", MainPage),
    ("/update-database", UpdateDatabase),
    ("/login", LoginPage)
], debug=True)
