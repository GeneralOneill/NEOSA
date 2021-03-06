#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#author Joe Tan
import webapp2
import jinja2
import json
import os
import logging
from datetime import datetime
from google.appengine.api import users
from neosa import *


# sets system Environment
jinja_environment = jinja2.Environment(
  loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

# sets user to active
class setUserActive(webapp2.RequestHandler):
    def get(self):
        user = getCurrentUser().get()
        user.isActive = True
        user.put()

# sets user to inactive
class setUserInActive(webapp2.RequestHandler):
    def get(self):
        user = getCurrentUser().get()
        user.isActive = False
        user.put()

class addFriend(webapp2.RequestHandler):
    def post(self):
        user = getCurrentUser().get()
        blob = self.request.get('username')
        username = json.loads(blob)
        if username not in user.friends:
            user.friends.append(username)
            user.put()

# handles the rendering of the homepage
# checks if the user is logged in
# if the user is not logged it, they have less privilages
class MainHandler(webapp2.RequestHandler):
    def get(self):
        # gets the currentUser
        user = getCurrentUser()
        current_user = {'current_user':'Stranger'}
        if user:
            # gets the html that would compose the page
            template = jinja_environment.get_template('templates/index.html')
            # gets the user's firstname to be displayed
            first_name = user.get().first_name
            if first_name:
                current_user['current_user'] = first_name
                # renders the html page with Jinja2
            self.response.out.write(template.render(current_user))
        else:
            # if user is not logged in they are rendered a different page
            template = jinja_environment.get_template('templates/index0.html')
            self.response.out.write(template.render(current_user))

# renders the map page
# handles the post requests from the map page
class MapHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        template = jinja_environment.get_template('templates/map.html')
        if user:
            template = jinja_environment.get_template('templates/map.html')
            username = getCurrentUser().get().username
            # renders the map page
            self.response.out.write(template.render({"username": username}))
        else:
            # if the user is not logged in
            # they are sent to the loging handler to log them in
            self.redirect('/login')
    def post(self):
        user = users.get_current_user()
        if user:
            # gets the latlng of the user
            # adds it to the database based on the user
            blob = self.request.get('json')
            latlng =  json.loads(blob)
            user = getCurrentUser().get()
            user.latlng = latlng
            # logging.error(user.latlng)
            user.put()

# handles the get requests from map page
class UsersHandler(webapp2.RequestHandler):
    def get(self):
        # sets the handler to send json data
        self.response.headers['Content-Type'] = 'application/json';
        # add latlng data to a dicitonary
        obj = {'userInfoArray': getAllOtherActiveUsersLatLng()}
        # sends the data to the map page
        self.response.out.write(json.dumps(obj))

# logs the user out
class LogoutHandler(webapp2.RequestHandler):
    def get(self):
        setCurrentUserInactive()
        self.redirect(users.create_logout_url('/'))

# logs the user in
class LoginHandler(webapp2.RequestHandler):
    def get(self):
        # redirects the user to the profile page after login
        self.redirect(users.create_login_url('/profile'))

class ScheduleHandler(webapp2.RequestHandler):
    def get(self):
        user = getCurrentUser().get()
        template = jinja_environment.get_template('templates/schedule.html')
        self.response.out.write(template.render({"user":user}))
    def post(self):
        user = users.get_current_user()
        user = getCurrentUser().get()
        data = json.loads(self.request.body);
        schedule = data["schedule"];
        #Make python friendly date objects
        dates = [datetime.strptime(dateString, "%a, %d %b %Y %H:%M:%S %Z") for dateString in schedule]
        #store these in user
        user.schedule = dates
        user.put()

# Handles POST requests from the progile page
# uses the data from post to update the user's information in the database
class ProfileHandler(webapp2.RequestHandler):
    def get(self):
        user = getCurrentUser()
        if user:
            first_name = user.get().first_name
            if first_name:
                # is the user is in database
                # redirects the user to the subject page
                self.redirect('/subject')
        # rendes the progile page
        template = jinja_environment.get_template('templates/profile.html')
        self.response.out.write(template.render())
    # handles the post request
    def post(self):
        user = users.get_current_user()
        user_id = user.user_id()
        username = self.request.get("username")
        first_name = self.request.get("first_name")
        last_name = self.request.get("last_name")
        major = self.request.get("major")
        email_address = user.email()
        createUser(user_id,username, major, first_name, last_name, email_address)
        self.redirect('/subject')

# reders the subject page
# handles post request add the subject the user select
# updates the database
class SubjectHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('templates/subject.html')
        self.response.out.write(template.render())
    def post(self):
        user = getCurrentUser().get()
        user.subject = self.request.get("subject")
        user.put()
        self.redirect('/')

# experimental page that is still underdevelopment
class ProfilePageHandler(webapp2.RequestHandler):
    def get(self):
        user = getCurrentUser().get()
        #this gets all the user information so that the page can be dynamic
        if user:
            #if the user is logged on then we can call all of the user properties
            template = jinja_environment.get_template('templates/profilepage.html')
            self.response.out.write(template.render({"user":user}))
            #we are sending the user dictionary as an object to the profile page
    def post(self):
        user = getCurrentUser().get()
        user.first_name = self.request.get("first_name")
        user.last_name = self.request.get("last_name")
        user.major = self.request.get("major")
        user.subject = self.request.get("subject")
        user.put()
        # self.response.out.write(user.first_name)
        self.redirect('/profilepage')

# display the profilepage of a friend
class FriendXHandler(webapp2.RequestHandler):
    def get(self):
        # gets friends user name
        username = self.request.get('username')
        user = getUser(username).get()
        #this gets all the user information so that the page can be dynamic
        template = jinja_environment.get_template('templates/friendX.html')
        self.response.out.write(template.render({"user":user}))
        #we are sending the user dictionary as an object to the profile page

# sets the pointers to the appropriate class
# ie the path in the url
app = webapp2.WSGIApplication([
    ('/map', MapHandler),
    ('/users', UsersHandler),
    ('/profile', ProfileHandler),
    ('/profilepage', ProfilePageHandler),
    ('/login', LoginHandler),
    ('/schedule', ScheduleHandler),
    ('/setActive', setUserActive),
    ('/setInactive', setUserInActive),
    ('/logout', LogoutHandler),
    ('/subject', SubjectHandler),
    ('/addFriend', addFriend),
    ('/friendX', FriendXHandler),
    ('/.*', MainHandler)
], debug=True)
