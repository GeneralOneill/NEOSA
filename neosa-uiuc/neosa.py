# Author Joe Tan
from google.appengine.ext import ndb
from google.appengine.api import users


# The User class with all of its properties
class UserModel(ndb.Model):
    user_id = ndb.StringProperty(required = True)
    username = ndb.StringProperty()
    major = ndb.StringProperty()
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    email_address = ndb.StringProperty()
    latlng = ndb.JsonProperty()
    subject = ndb.StringProperty()
    schedule = ndb.DateTimeProperty(repeated = True)
    isActive = ndb.BooleanProperty()
    friends = ndb.PickleProperty(repeated = True)

# returns the unique key for the current user acessing the site
# key and ids are very different things
# key can get all the properties of the users,
# while the id can get the perspective key in the database
def getCurrentUser():
    key = False
    # get the current user's unique id
    user = users.get_current_user()
    if user:
        # searches the database to fetch the users's unique key
        # returns a list
        user = UserModel.query(UserModel.user_id == user.user_id()).fetch(keys_only=True)
        # if the search returns a none empty list
        # ie finding the perspective user
        # it will set the varaiable key to the value of the unique key.
        if len(user) > 0:
            key = user[0]
    return key

# create a user class and initalizes its properties,
# then stores the user into the database
def createUser(user,username, major, first_name, last_name, email_address):
    user = UserModel(user_id = user, username = username, major = major, first_name = first_name, last_name =last_name, email_address = email_address)
    user.put()

# returns a list containing all user's latlngs

def getAllUsersLatLng():
    # search the data base for all users
    keys = UserModel.query().fetch(keys_only=True)
    userInfoArray = []
    for key in keys:
        user = key.get()
        # stores the latlng in a dictionary with the user id as key and latlng as the value
        userInfoArray.append({"user_id":str(user.user_id), "latlng": user.latlng, "username": user.username, "subject": user.subject})
    return userInfoArray

# returns all of the all active user's latlng excluding the current user that is logged on
def getAllOtherActiveUsersLatLng():
    user = users.get_current_user()
    # searches the database with active users
    # and return their unique keyss
    keys = UserModel.query(UserModel.isActive == True, UserModel.user_id != user.user_id()).fetch(keys_only=True)
    userInfoArray = []
    for key in keys:
        user = key.get()
        # adds the user to a dictionary, using id as the key, and the key as the value
        userInfoArray.append({"user_id":str(user.user_id), "latlng": user.latlng, "username": user.username, "subject": user.subject})
    return userInfoArray

# changes the current user's isActive propertie to true
def setCurrentUserActive():
    # gets the current user
    user = getCurrentUser().get()
    # changes the user's isActive propertie to true
    user.isActive = True
    user.put()

# changes the current user's isActive propertie to false
def setCurrentUserInactive():
    # gets the current user
    user = getCurrentUser().get()
    # changes the user's isActive propertie to false
    user.isActive = False
    user.put()

# adds a friend given a user name
def addFriend(username):
    logging.error(username)
    other = UserModel.query(UserModel.username == username).fetch(keys_only = True)
    user = getCurrentUser().get()
    if(len(other) > 0 and other not in user.friends):
        user.friends.append(other[0])
        user.put()

def getFriends():
    user = getCurrentUser().get()
    return user.friends
