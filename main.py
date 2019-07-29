import webapp2
import logging
import jinja2
import os
from google.appengine.ext import ndb
from google.appengine.api import users


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
current_user = users.get_current_user()

class GetStartedPage(webapp2.RequestHandler):
    def get(self):
        name = self.request.get("name") or "World"


        # movie_query = Movie.query().order(-Movie.rating)
        # movies = movie_query.fetch()


        template_vars = {
            "creators" : creators,
            "name" : name,
        }

        template = jinja_env.get_template("templates/get-started.html")
        self.response.write(template.render(template_vars))


class LoginPage(webapp2.RequestHandler):
    def get(self):

        email_address = current_user.email()
        in_database = Profile.query().filter(Profile.email==email_address).get()
        print in_database

        if in_database:
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


        template_vars = {
            "creators" : creators,
            "name" : name,
            "current_user" : current_user,
        }

        current_user

        template = jinja_env.get_template("templates/main.html")
        self.response.write(template.render(template_vars))

class UpdateDatabase(webapp2.RequestHandler):
    def get(self):
        template = jinja_env.get_template("templates/update-database.html")
        self.response.write(template.render())

        print("Hello")

    def post(self):
        interest = self.request.get("input-interest")
        Interest(
            interest_name = interest,
            interest_description = "",
        ).put()
        self.redirect("/main")




app = webapp2.WSGIApplication([
    ("/", GetStartedPage),
    ("/main", MainPage),
    ("/update-database", UpdateDatabase),
    ("/login", LoginPage)
], debug=True)
