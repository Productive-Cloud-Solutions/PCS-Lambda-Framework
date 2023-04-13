import os
import json
import boto3
# from models import user_old as user_model
from pcs.models.user import User
from pcs.util.stripe import stripe
from datetime import datetime
from pcs.decorators.checkUser import check_user
from pcs.controllers.baseController import BaseController

client = boto3.client('cognito-idp')

user_model = User()

class UserController(BaseController):
    def getUser(self):
        if not self.userId:
            raise Exception("User was not found")
        if not self.payload.get("username"):
            raise Exception("Username was not found")
        
        user= user_model.get(self.userId) 
        if not user:
            raise Exception("User was not found!!!")
        
        query= {
            'userId': self.userId,
            # 'username': self.payload['username'],
        }
        
        user= user_model.find(query) 
        if not user:
            raise Exception("Failed to find user!!!")
        return user


    def createUser(self):
        if not self.userId:
            raise Exception("User was not found")
        if not self.payload.get("username"):
            raise Exception("Username cannot be empty!!!") 
        if not self.payload.get("email"):
            raise Exception("Email cannot be empty!!!")    
        # if not self.payload.get("UserCreateDate"):
        #     raise Exception("UserCreateDate cannot be empty!!!")
        self.payload['userId']=self.userId
        
        user = user_model.create(self.payload)
        if not user:
            raise Exception("Failed to create user!!!")
        
        return user


    def updateUser(self):
        if not self.userId:
            raise Exception("User was not found")
        user = user_model.get(self.userId)
        if not user:
            raise Exception("User was not found!!!")
        
        query= {
            'userId': self.userId,
            'username': self.payload['user']['username'],
        }
        
        user = user_model.find(query)
        if not user:
            raise Exception("User was not found!!!")
        
        user.update(self.payload['user'])
        
        user= user_model.replace(user['id'],user)
        if not user:
            raise Exception("Failure to update")
        
        return user
    
    def deleteUser(self):
        if not self.userId:
            raise Exception("User was not found")

        user= user_model.get(self.userId) 
        if not user:
            raise Exception("User was not found!!!")
        
        user = user_model.delete(self.payload.get("userId"))
        
        if not user:
            return True
        
        return user