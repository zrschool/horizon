import webapp2
import logging
import jinja2
import os
from google.appengine.ext import ndb
from google.appengine.api import users


class User(ndb.Model):
    email = ndb.StringProperty()
    interests = ndb.KeyProperty(repeated = True)


class Interest(ndb.Model):
    interest_name = ndb.StringProperty()
    interest_description = ndb.StringProperty()


class Movie(ndb.Model):
    """
    title: string for the movie title
    length: int for number of minutes
    rating: float 0.0-5.0 for rating of movie
    """
    title = ndb.StringProperty(required=True)
    runtime = ndb.IntegerProperty(required=True)
    rating = ndb.FloatProperty(required=False, default=0)

    def describe(self):
        """
        return a string describing the movie
        """
        return "%s is %d minutes long and has a rating of %f" % (self.title, self.runtime, self.rating)



jinja_env = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.dirname(__file__))
)

creators = "Asia Collins, Bethelehem Engeda, Zachary Rideaux, and Isabella Siu"

class GetStartedPage(webapp2.RequestHandler):
    def get(self):
        name = self.request.get("name") or "World"


        # movie_query = Movie.query().order(-Movie.rating)
        # movies = movie_query.fetch()

        current_user = users.get_current_user()
        signin_link = users.create_login_url("/")

        template_vars = {
            "creators" : creators,
            "name" : name,
        }

        template = jinja_env.get_template("templates/get-started.html")
        self.response.write(template.render(template_vars))

class MainPage(webapp2.RequestHandler):
    def get(self):
        name = self.request.get("name") or "World"

        current_user = users.get_current_user()
        signin_link = users.create_login_url("/")

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
        # lionking2 = Movie(
        #     title = "Lion King 2",
        #     runtime = 122,
        #     rating = 3.5,
        #     star_keys = [dylan_sprouse_key, cole_sprouse_key, atsuko_kagari_key])

        # TODO: Make new interest with user input
        # TODO: .put() the new interest in the database and assign it to the user

        template = jinja_env.get_template("templates/update-database.html")
        self.response.write(template.render())
        self.redirect("/main")

        print("Hello")


app = webapp2.WSGIApplication([
    ("/", GetStartedPage),
    ("/main", MainPage),
    ("/update-database", UpdateDatabase),
], debug=True)
