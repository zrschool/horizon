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
    recommendations = ndb.KeyProperty(
        kind = Interest,
        repeated = True,
    )


def get_random_profiles(user_profile):
    """
    Takes a profile (user_profile) and generates a random list of other
    profiles in the database
    """
    selected_interests = user_profile.selected_interests
    user_email = user_profile.email
    all_profiles = Profile.query().filter(Profile.email!=user_email).fetch()
    random_profiles = []
    for i in range(3):
        random_profiles.append(all_profiles[random.randrange(len(all_profiles))])
    print "RANDOM PROFILES: " + str(random_profiles)
    return random_profiles


def compare_interests(user_profile, random_profiles):
    """
    Given the user's profile, compare it to a list of randomly selected
    profiles. A dictionary item of scores is made for each profile. A score is
    determined for each comparison based on how many mutual interests there are
    between user_profile and the random profile. Return the profile with the
    highest score
    """
    email_profile_pairs = {}
    email_score_pairs = {}
    # Assign scores to each of the random profiles
    for profile in random_profiles:
        profile_score = 0
        for interest in profile.interests:
            if interest in user_profile.selected_interests:
                profile_score += 1
        email_profile_pairs.update({profile.email : profile})
        email_score_pairs.update({profile.email : profile_score})
    # Get dict item with highest score
    # print email_profile_pairs
    # print email_score_pairs

    highest_scorer = max(email_score_pairs, key=email_score_pairs.get)
    print(highest_scorer, email_score_pairs[highest_scorer])
    highest_scorer_profile = email_profile_pairs.get(highest_scorer)
    return highest_scorer_profile


def get_recommendations(user_profile, highest_scorer_profile):
    """
    Removes all mutual interests from highest scorer's interests to return
    non-mutual interests
    """
    selected_interests = user_profile.selected_interests
    other_users_interests = highest_scorer_profile.interests
    non_mutual_interests = []
    for i in range(len(other_users_interests)):
        non_mutual_interests.append(other_users_interests[i])
    print "BEFORE " + str(non_mutual_interests)
    for interest in selected_interests:
        if interest in other_users_interests:
            non_mutual_interests.remove(interest)
        # if interest in user_profile.interests:
        #     non_mutual_interests.remove(interest)
    print "AFTER " + str(non_mutual_interests)
    return non_mutual_interests


def clear_existing_recommendations(current_profile):
    del current_profile.recommendations[:]
    current_profile.put()

def clear_interests(current_profile):
    del current_profile.interests[:]
    current_profile.put()

def clear_selected_interests(current_profile):
    del current_profile.selected_interests[:]
    current_profile.put()


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

        self.redirect("/main?key=" + current_profile_key.urlsafe())


class GetRecommendations(webapp2.RequestHandler):
    def post(self):
        current_user = users.get_current_user()
        current_profile = Profile.query().filter(Profile.email==current_user.email()).get()
        current_profile_key = current_profile.key

        clear_existing_recommendations(current_profile)
        random_profiles = get_random_profiles(current_profile)
        highest_scorer_profile = compare_interests(current_profile, random_profiles)
        recommendations = get_recommendations(current_profile, highest_scorer_profile)
        for recommendation in recommendations:
            print recommendation
            current_profile.recommendations.append(recommendation)

        current_profile.put()
        # Redirect to main
        self.redirect("/main?key=" + current_profile_key.urlsafe())


class ClearRecommendations(webapp2.RequestHandler):
    def post(self):
        current_user = users.get_current_user()
        current_profile = Profile.query().filter(Profile.email==current_user.email()).get()
        current_profile_key = current_profile.key

        clear_existing_recommendations(current_profile)

        current_profile.put()
        # Redirect to main
        self.redirect("/main?key=" + current_profile_key.urlsafe())

class ClearInterests(webapp2.RequestHandler):
    def post(self):
        current_user = users.get_current_user()
        current_profile = Profile.query().filter(Profile.email==current_user.email()).get()
        current_profile_key = current_profile.key

        clear_interests(current_profile)
        clear_selected_interests(current_profile)

        current_profile.put()
        # Redirect to main
        self.redirect("/main?key=" + current_profile_key.urlsafe())


class ClearSelectedInterests(webapp2.RequestHandler):
    def post(self):
        current_user = users.get_current_user()
        current_profile = Profile.query().filter(Profile.email==current_user.email()).get()
        current_profile_key = current_profile.key


        clear_selected_interests(current_profile)

        current_profile.put()
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
    ("/get-recommendations", GetRecommendations),
    ("/clear-recommendations", ClearRecommendations),
    ("/clear-selected-interests", ClearSelectedInterests),
    ("/clear-interests", ClearInterests),
    ("/login", LoginPage),
    ("/about-us", AboutUsPage),
], debug=True)
