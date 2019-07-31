import webapp2
import logging
import jinja2
import os
import random
from google.appengine.ext import ndb
from google.appengine.api import users


class Interest(ndb.Model):
    interest_name = ndb.StringProperty()
    interest_description = ndb.StringProperty()


class Profile(ndb.Model):
    email = ndb.StringProperty()
    interests = ndb.KeyProperty(
        kind = Interest,
        repeated = True
    )
    selected_interests = ndb.KeyProperty(
        kind = Interest,
        repeated = True,
    )


def compare_users(user_profile):
    """
    Takes a profile (user_profile) and compares its selected interests to
    other profiles in the database. A score is determined for each comparison
    based on how many mutual interests there are
    """
    selected_interests = user_profile.selected_interests
    user_score_pairs = {}
    



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
    def post(self):
        current_user = users.get_current_user()
        current_profile = Profile.query().filter(Profile.email==current_user.email()).get()
        current_profile_key = current_profile.key

        # Update 'Your Current Interests' with input box
        input_interest = self.request.get("input-interest").lower()
        if input_interest:
            interest = Interest.query().filter(Interest.interest_name == input_interest).get()
            print interest
            if interest:
                interest_key = interest.key
            else:
                interest = Interest(
                    interest_name = input_interest,
                    interest_description = "",
                )
                interest_key = interest.put()
            # Append new Interest to Profile Interests list
            if interest_key not in current_profile.interests:
                current_profile.interests.append(interest_key)
                current_profile_key = current_profile.put()

        # Places interests in 'Selected Interests', but prevents duplicates
        interest_key = self.request.get("interest_key")
        if interest_key:
            interest_key = ndb.Key(urlsafe=interest_key)
            if interest_key in current_profile.selected_interests:
                current_profile.selected_interests.remove(interest_key)
                print interest_key.get().interest_name + " removed from selected interests"
            else:
                current_profile.selected_interests.append(interest_key)
                print interest_key.get().interest_name + " added to selected interests"

            current_profile_key = current_profile.put()

        # TODO: function that takes in current_profile and compares its selected
        #       interests to others in the database
        compare_users(current_profile)

        # Redirect to main
        self.redirect("/main?key=" + current_profile_key.urlsafe())


class AboutUsPage(webapp2.RequestHandler):
    def get(self):
        template_vars = {
            "creators" : creators,
        }

        template = jinja_env.get_template("templates/about-us.html")
        self.response.write(template.render(template_vars))


app = webapp2.WSGIApplication([
    ("/", GetStartedPage),
    ("/main", MainPage),
    ("/update-database", UpdateDatabase),
    ("/login", LoginPage),
    ("/about-us", AboutUsPage),
], debug=True)
