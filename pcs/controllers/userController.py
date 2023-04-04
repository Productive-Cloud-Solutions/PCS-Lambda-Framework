import os
import json
import boto3
# from models import user_old as user_model
from models.user import User
from util.stripe import stripe
from datetime import datetime
from decorators.checkUser import check_user
from framework.baseController import BaseController

client = boto3.client('cognito-idp')

user_model = User()

# class UserController(BaseController):
#     def __init__(self, userId=None, username=None, payload=None, source=None):
#         super.__init__(self, userId, username, payload, source)

#     def userInit(self):
#         user = getUser(self.userId, self.username)
#         return user

def getUser(userId, username=False):
    user = user_model.get(userId)
    # unknown exception
    if not user:
        if not username:
            raise Exception("Can't Find User!!!")
        return createUser(userId, username)

    return user


def createUser(userId, username):
    poolId = os.environ.get('USER_POOL')
    user = {
        'id':userId
    }
    # if local dev enviroment 
    if os.environ.get('AWS_SAM_LOCAL'):
        user['created'] = datetime.today().replace(microsecond=0)
        user['modified'] = datetime.today().replace(microsecond=0)
        user['username'] = username if username else 'username_'+user['id']
        if 'email' not in user:
            user['email'] = user['username']+"@gmail.com"
    else:
        # get cognito data
        result = client.admin_get_user(
            UserPoolId= poolId,
            Username=username
        )
        if 'UserAttributes' not in result:
            raise Exception("Can't find user in the system")
        email = False
        user['created'] = int(result['UserCreateDate'].timestamp())
        user['modified'] = int(result['UserLastModifiedDate'].timestamp())
        # find user email address
        for attr in result['UserAttributes']:
            if attr['Name'] != 'email':
                continue # skip
            email = attr['Value']

        # Build data 
        user['username'] = username
        if email:
            user['email'] = email

    #set defaults 
    user['approved'] = False
    
    return user_model.create(user)


def updateUser(userId,data,username):
    user = user_model.get(userId)
    # unknown exception
    if not user:
        if not username:
            raise Exception("Can't Find User!!!")
        user = createUser(userId, username)

    user.update(data)
    
    return user_model.replace(userId, user)



def adminUpdateUser(userId,data,adminUsername):
    pass