# test for notes API
import os
import app
import uuid
import boto3
import unittest
import time
import random
from pcs.controllers.recordController import RecordController
from datetime import datetime
from unittest.mock import patch, MagicMock, Mock
from pcs.frameworks.appFrameworks import GQLServerlessApp

from pcs.testing.test_creator import TestUser, createEvent, LambdaTester, loadSample, createUser

tester = LambdaTester(app.lambda_handler)

class GeneralTest(unittest.TestCase):


    def setUp(self):
        self.user = createUser(TestUser())
        self.gqlApp= GQLServerlessApp(userId=self.user.id,username=None, payload= None, source=None)
        self.gqlApp.linkGraphQL(RecordController, None)

    def test_create(self):
        payload= {}
        payload['name']= 'Record Name'
        payload['description']= 'Record Description'
        payload['file']= "file.txt"
        
        self.gqlApp.payload=payload
        
        result = self.gqlApp.run(None, "createRecord")
        self.assertIn("id", result, 'id was not in result')
        self.assertEqual(payload['name'], result['name'], 'name was not correct')
        self.assertEqual(payload['description'], result['description'], 'description was not correct')
        self.assertEqual(payload['file'], result['file'], 'file was not correct')
        
        payload= {}
        payload['name']= 'Record Name'
        payload['description']= 'Record Description'
        payload['file']= "file.txt"
        payload['userId']=result['id']
        
        result = self.gqlApp.run(None, "createRecord")
        self.assertIn("userId", result, 'User was not found')
        self.assertEqual(payload['name'], result['name'], 'name was not correct')
        self.assertEqual(payload['description'], result['description'], 'description was not correct')
        self.assertEqual(payload['file'], result['file'], 'file was not correct')
        
        payload= {}
        payload['name']= ''
        payload['description']= 'Record Description'
        payload['file']= "file.txt"
        payload['userId']=result['id']
        
        result = self.gqlApp.run(None, "createRecord")
        self.assertIn("name", result, 'Name cannot be empty!!!')
        self.assertEqual(payload['description'], result['description'], 'description was not correct')
        self.assertEqual(payload['file'], result['file'], 'file was not correct')
        
    def test_update(self):
        payload= {}
        payload['name']= 'Record Name'
        payload['description']= 'Record Description'
        payload['file']= "file.txt"
        
        self.gqlApp.payload=payload
        
        result = self.gqlApp.run(None, "createRecord")
        self.assertIn("id", result, 'id was not in result')
        self.assertEqual(payload['name'], result['name'], 'name was not correct')
        self.assertEqual(payload['description'], result['description'], 'description was not correct')
        self.assertEqual(payload['file'], result['file'], 'file was not correct')
        
        payload= {}
        payload['recordId'] = result['id']
        payload['record'] = {}
        payload['record']['name']= 'Record Name'
        payload['record']['description']= 'Record Description'
        payload['record']['file']= "file.txt"
        
        self.gqlApp.payload=payload

        result = self.gqlApp.run(None, "updateRecord")
        self.assertIn("id", result, "Name was not passed")      
        self.assertEqual(payload['record']['name'], result['name'], 'name was not correct')
        self.assertEqual(payload['record']['description'], result['description'], 'description was not correct')
        self.assertEqual(payload['record']['file'], result['file'], 'file was not correct')
        
    def test_delete(self):
        payload= {}
        payload['name']= 'Record Name'
        payload['description']= 'Record Description'
        payload['file']= "file.txt"
        
        self.gqlApp.payload=payload
        
        result = self.gqlApp.run(None, "createRecord")
        self.assertIn("id", result, 'id was not in result')
        self.assertEqual(payload['name'], result['name'], 'name was not correct')
        self.assertEqual(payload['description'], result['description'], 'description was not correct')
        self.assertEqual(payload['file'], result['file'], 'file was not correct')
        
        payload= {}
        payload['recordId'] = result['id']
        
        self.gqlApp.payload=payload

        result = self.gqlApp.run(None, "deleteRecord")
        self.assertEqual(payload['recordId'], result["id"], 'id was not in result')

        
        
    def test_retrieval(self):
        payload= {}
        payload['name']= 'Record Name'
        payload['description']= 'Record Description'
        payload['file']= "file.txt"
        
        self.gqlApp.payload=payload
        
        result = self.gqlApp.run(None, "createRecord")
        self.assertIn("id", result, 'id was not in result')
        self.assertEqual(payload['name'], result['name'], 'name was not correct')
        self.assertEqual(payload['description'], result['description'], 'description was not correct')
        self.assertEqual(payload['file'], result['file'], 'file was not correct')
        
        payload= {}
        payload['recordId'] = result['id']
        payload['record'] = {}
        payload['record']['name']= 'Record Name'
        payload['record']['description']= 'Record Description'
        payload['record']['file']= "file.txt"

        self.gqlApp.payload=payload

        result = self.gqlApp.run(None, "getRecord")
        self.assertIn("id", result, 'id was not in result')
        self.assertEqual(payload['record']['name'], result['name'], 'name was not correct')
        self.assertEqual(payload['record']['description'], result['description'], 'description was not correct')
        self.assertEqual(payload['record']['file'], result['file'], 'file was not correct')
        
    def test_retrievals(self):
        payload= {}
        payload['name']= 'Record Name'
        payload['description']= 'Record Description'
        payload['file']= "file.txt"
        
        self.gqlApp.payload=payload
        
        result = self.gqlApp.run(None, "createRecord")
        self.assertIn("id", result, 'id was not in result')
        self.assertEqual(payload['name'], result['name'], 'name was not correct')
        self.assertEqual(payload['description'], result['description'], 'description was not correct')
        self.assertEqual(payload['file'], result['file'], 'file was not correct')
        
        payload= {}
        payload['recordId'] = result['id']
        
        self.gqlApp.payload=payload

        result = self.gqlApp.run(None, "getRecords")
        self.assertEqual(1, len(result), "Wrong number of things passed back")


    def test_errors(self):
        pass


    @patch('pcs.util.appFileManager.create_presigned_url')
    def test_with_patch(self, patch_s3_generate_url):
        pass
