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
import datetime
from datetime import datetime
from google.appengine.api import users
from neosa import *

jinja_environment = jinja2.Environment(
  loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class Test(webapp2.RequestHandler):
    def get(self):
        user = getCurrentUser().get()
        for date in user.schedule:
            self.response.out.write('%s --- ' %(date))
        # template = jinja_environment.get_template('templates/subject.html')
        # self.response.out.write(template.render())

class MainHandler(webapp2.RequestHandler):
    def get(self):
        user = getCurrentUser()
        current_user = {'current_user':'Stranger'}
        if user:
            template = jinja_environment.get_template('templates/index.html')
            first_name = user.get().first_name
            if first_name:
                current_user['current_user'] = first_name
            self.response.out.write(template.render(current_user))
        else:
            template = jinja_environment.get_template('templates/index0.html')
            self.response.out.write(template.render(current_user))

class MapHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        template = jinja_environment.get_template('templates/map.html')
        if user:
            latlng = {'latlng':json.dumps(getAllUsersLatLng())}
            self.response.out.write(template.render(latlng))
        else:
            self.redirect('/login')
    def post(self):
        user = users.get_current_user()
        if user:
            blob = self.request.get('json')
            latlng =  json.loads(blob)
            user = getCurrentUser().get()
            user.latlng = latlng
            logging.error(user.latlng)
            user.put()

class UsersHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'application/json'
        obj = {'latlngArray': getAllUsersLatLng()}
        self.response.out.write(json.dumps(obj))


class LogoutHandler(webapp2.RequestHandler):
    def get(self):
        self.redirect(users.create_logout_url('/'))

class LoginHandler(webapp2.RequestHandler):
    def get(self):
        self.redirect(users.create_login_url('/profile'))

class Schedule(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'application/json'
        schedule_object = {"schedule" : getAllUsersSchedule()}

        # self.response.out.write(json.dumps(schedule_object))
        # for part in schedule_object:
        #     ref_dict =  {"schedule": [{"id": id }]}
        # self.response.out.write(ref_difeguct)
        # schedule = getAllUsersSchedule()
        # {"schedule" : [DateTime]}
        # of the dictionary
        #
        # compare the time however you like,
        # store it in a dictionary or a list
        # make a schedule_object, which is a dictionary
        self.response.out.write(schedule_object)


    def get_times(fileName):
          schedule_dict = json.load(fileName)
          dateTimes = []
          each_schedule = schedule_dict["schedule"]
          for schedule in each_schedule:
             dateTimes += schedule["schedule"]
          return dateTimes
          self.response.out.write(dateTimes)



class ScheduleHandler(webapp2.RequestHandler):
    def get(self):
        user = getCurrentUser()
        current_user = {'current_user':'Stranger'}
        first_name = user.get().first_name
        current_user['current_user'] = first_name
        template = jinja_environment.get_template('templates/schedule.html')
        self.response.out.write(template.render(current_user))
    def post(self):
        user = users.get_current_user()
        if user:
            user = getCurrentUser().get()
            data = json.loads(self.request.body);
            schedule = data["schedule"];
            #Make python friendly date objects
            dates = [datetime.strptime(dateString, "%a, %d %b %Y %H:%M:%S %Z") for dateString in schedule]
            #store these in user
            user.schedule = dates
            user.put()
            logging.error(dates)


class ProfileHandler(webapp2.RequestHandler):
    def get(self):
        user = getCurrentUser()
        if user:
            first_name = user.get().first_name
            if first_name:
                self.redirect('/subject')
        template = jinja_environment.get_template('templates/profile.html')
        self.response.out.write(template.render())
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

class SubjectHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('templates/subject.html')
        self.response.out.write(template.render())
    def post(self):
        user = getCurrentUser().get()
        user.subject = self.request.get("subject")
        user.put()
        self.redirect('/')

app = webapp2.WSGIApplication([
    ('/map', MapHandler),
    ('/users', UsersHandler),
    ('/profile', ProfileHandler),
    ('/login', LoginHandler),
    ('/schedule', ScheduleHandler),
    ('/test', Test),
    ('/logout', LogoutHandler),
    ('/subject', SubjectHandler),
    ('/schedule_test', Schedule),
    ('/.*', MainHandler)
], debug=True)
