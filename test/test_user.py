# test for notes API
import os
import app
import uuid
import boto3
import unittest
import time
import random
from datetime import datetime
from pcs.models.user import User
from pcs.controllers.userController import UserController
from unittest.mock import patch, MagicMock, Mock
from pcs.frameworks.appFrameworks import GQLServerlessApp

from pcs.testing.test_creator import TestUser, createEvent, createUser, LambdaTester


tester = LambdaTester(app.lambda_handler)
user_model = User()

class GeneralTest(unittest.TestCase):

    def setUp(self):
        self.user = createUser(TestUser())
        self.gqlApp= GQLServerlessApp(userId=self.user.id,username=None, payload= None, source=None)
        self.gqlApp.linkGraphQL(UserController, None)


    def test_create(self):
        payload= {}
        payload['username']= 'Username'
        payload['email']= 'Email@gmail.com'
        
        self.gqlApp.payload=payload
        
        result = self.gqlApp.run(None, "createUser")
        self.assertEqual(payload['username'], result['username'], 'username was not correct')
        self.assertEqual(payload['email'], result['email'], 'email was not correct')
        
    def test_update(self):
        payload= {}
        payload['username']= 'Username'
        payload['email']= 'Email@gmail.com'
        
        self.gqlApp.payload=payload
        
        result = self.gqlApp.run(None, "createUser")
        self.assertEqual(payload['username'], result['username'], 'username was not correct')
        self.assertEqual(payload['email'], result['email'], 'email was not correct')
        
        payload= {}
        payload['user']={}
        payload['user']['username']= 'Username'
        payload['user']['email']= 'Email@gmail.com'
        
        self.gqlApp.payload=payload

        result = self.gqlApp.run(None, "updateUser")
        self.assertEqual(payload['user']['username'], result['username'], 'username was not correct')
        self.assertEqual(payload['user']['email'], result['email'], 'email was not correct')
        
    def test_delete(self):
        payload= {}
        payload['username']= 'Username'
        payload['email']= 'Email@gmail.com'
        
        self.gqlApp.payload=payload
        
        result = self.gqlApp.run(None, "createUser")
        self.assertEqual(payload['username'], result['username'], 'username was not correct')
        self.assertEqual(payload['email'], result['email'], 'email was not correct')
        
        payload= {}
        payload['userId'] = result['id']
        
        self.gqlApp.payload=payload

        result = self.gqlApp.run(None, "deleteUser")
        self.assertEqual(payload['userId'], result["id"], 'id was not in result')


    def test_retrieval(self):
        payload= {}
        payload['username']= 'Username'
        payload['email']= 'Email@gmail.com'
        
        self.gqlApp.payload=payload
        
        result = self.gqlApp.run(None, "createUser")
        self.assertEqual(payload['username'], result['username'], 'username was not correct')
        
        payload= {}
        payload['username']= 'Username'
        self.gqlApp.payload=payload

        result = self.gqlApp.run(None, "getUser")
        self.assertEqual(payload['username'], result['username'], 'username was not correct')
        

    def test_errors(self):
        pass
        # payload = {}
        # payload['categories'] = ['Wrong Code']
        # with self.assertRaises(Exception) as error:
        #     result = tester.createEvent("getTranscript", user=self.user,
        #                             _id=False, modifiedTimeStamp=False, payload= payload)
        # self.assertIn('The code is not valid',
        #               error.exception.args[0], 'Wrong Error received')

    @patch('pcs.util.appFileManager.create_presigned_url')
    def test_with_patch(self, patch_s3_generate_url):
        pass

        # # stubbing s3 mocked service function for testing
        # patch_s3_generate_url.return_value = 'https://s3.amazonaws.com/app-bucket/test/obj.jpg'