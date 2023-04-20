# test for notes API
import os
import app
import uuid
import inspect
import boto3
import unittest
import time
import random
from datetime import datetime
from unittest.mock import patch, MagicMock, Mock
from pcs.controllers.baseController import BaseController
from pcs.frameworks.appFrameworks import GQLServerlessApp

from pcs.testing.test_creator import TestUser, createEvent, LambdaTester, loadSample

tester = LambdaTester(app.lambda_handler)

class DummyController(BaseController):
    def getUserId(self):
        return self.userId
    
    def getUsername(self):
        return self.username
    
    def getPayload(self):
        return self.payload
    
    def getSource(self):
        return self.source
    
    def hello(self):
        return "Hello"
    
    def getKwargsArgs(self, *args, **kwargs):
        argsList = []
        for a in args:
            argsList.append(a)

        kwargsDict = {}
        for k, v in kwargs.items():
            kwargsDict[k] = v
        
        return argsList, kwargsDict
    
    def getKwargs(self, **kwargs):
        kwargsDict = {}
        for k, v in kwargs.items():
            kwargsDict[k] = v
        
        return kwargsDict
    
    def getArgs(self, *args):
        argsList = []
        for a in args:
            argsList.append(a)
        
        return argsList

class GeneralTest(unittest.TestCase):

    """
    This is where you set up things you will use across all test
    """
    def setUp(self):
        self.userId = str(uuid.uuid4())
        self.id = str(uuid.uuid4())
        self.username = self.userId+"_username"

        self.payload = {
            "key" :  self.id
        }
        self.source = {
            "key" :  self.id
        }

        self.args = [
            "test", "dummy", "work"
        ]
        
        self.kwargs = {
            "first": "design",
            "second": "testing",
            "third" : "deploy"
        }

        self.controlClass = DummyController
        self.instance = DummyController()
        self.gqlApp = GQLServerlessApp(userId=self.userId, username=self.username, payload=self.payload, source=self.source)
        # app = App(userId=userId, username=username, payload=data, source=event['source'])
        pass
        """
        Create a couple default users
        """
        # self.user = TestUser().createUser()
        # self.user2 = TestUser().createUser()
        # self.doctor = TestUser().createUser()
        # self.doctor2 = TestUser().createUser()

    #ControlClass will have something because it gets instantiated in run with params
    def test_class_no_params(self):
        self.gqlApp.linkGraphQL(self.controlClass)

        result = self.gqlApp.run("abcd", "hello")
        self.assertEqual("Hello", result, "None came back")
        
        #Test userId get
        result = self.gqlApp.run("abcd", "getUserId")
        self.assertEqual(self.userId, result, "Wrong result")

        #Test username get
        result = self.gqlApp.run("abcd", "getUsername")
        self.assertEqual(self.username, result, "Wrong result")

        #Test payload get
        result = self.gqlApp.run("abcd", "getPayload")
        self.assertEqual(self.payload, result, "Wrong result")
        
        #Test source get
        result = self.gqlApp.run("abcd", "getSource")
        self.assertEqual(self.source, result, "Wrong result")


    def test_class_params(self):
        self.gqlApp.linkGraphQL(self.controlClass, self.id, "hello", "hello")
        
        result = self.gqlApp.run(self.id, "hello")
        self.assertEqual("Hello", result, "None came back")
        
        #Test userId get
        result = self.gqlApp.run(self.id, "getUserId")
        self.assertEqual(self.userId, result, "Wrong result")
        
        #Test invalid mapping
        with self.assertRaises(Exception) as error:
            result = self.gqlApp.run(self.id+"invalid", "getUserId")
        self.assertEqual("Unmapped Action!", error.exception.args[0], "Wrong id passed")

        #Test username get
        result = self.gqlApp.run(self.id, "getUsername")
        self.assertEqual(self.username, result, "Wrong result")

        #Test payload get
        result = self.gqlApp.run(self.id, "getPayload")
        self.assertEqual(self.payload, result, "Wrong result")
        
        #Test source get
        result = self.gqlApp.run(self.id, "getSource")
        self.assertEqual(self.source, result, "Wrong result")
    

    def test_class_action_map(self):
        #These go to the None parentType
        self.gqlApp.linkGraphQL(self.controlClass, action=self.id+"hello", func="hello")
        self.gqlApp.linkGraphQL(self.controlClass, action=self.id+"getUserId", func="getUserId")
        self.gqlApp.linkGraphQL(self.controlClass, action=self.id+"getUsername", func="getUsername")
        self.gqlApp.linkGraphQL(self.controlClass, action=self.id+"getPayload", func="getPayload")
        self.gqlApp.linkGraphQL(self.controlClass, action=self.id+"getSource", func="getSource")

        #Goes to self.id+"source" ParentType
        self.gqlApp.linkGraphQL(self.controlClass, parentType=self.id+"source", action=self.id+"getSource", func="getSource")
        

        result = self.gqlApp.run(self.id+"hello", "hello")
        self.assertEqual("Hello", result, "None came back")
        
        #Test userId get
        result = self.gqlApp.run(self.id+"getUserId", "getUserId")
        self.assertEqual(self.userId, result, "Wrong result")

        #Test username get
        result = self.gqlApp.run(self.id+"getUsername", "getUsername")
        self.assertEqual(self.username, result, "Wrong result")

        #Test payload get
        result = self.gqlApp.run(self.id+"getPayload", "getPayload")
        self.assertEqual(self.payload, result, "Wrong result")
        
        #Test source get
        result = self.gqlApp.run(self.id+"getSource", "getSource")
        self.assertEqual(self.source, result, "Wrong result")

        result = self.gqlApp.run(self.id+"source", self.id+"getSource")
        self.assertEqual(self.source, result, "Wrong result")

    #All the methods should return None since instance has been instantiated with no params
    def test_instance_no_params(self):
        self.gqlApp.linkGraphQL(self.instance)
        result = self.gqlApp.run("abcd", "hello")
        self.assertEqual("Hello", result, "None came back")
        
        #Test userId get
        result = self.gqlApp.run("abcd", "getUserId")
        self.assertEqual(None, result, "Wrong result")

        #Test username get
        result = self.gqlApp.run("abcd", "getUsername")
        self.assertEqual(None, result, "Wrong result")

        #Test payload get
        result = self.gqlApp.run("abcd", "getPayload")
        self.assertEqual(None, result, "Wrong result")
        
        #Test source get
        result = self.gqlApp.run("abcd", "getSource")
        self.assertEqual(None, result, "Wrong result")
    
    def test_instance_params(self):
        self.instance = DummyController(userId=self.userId, username=self.username, payload=self.payload, source=self.source)
        self.gqlApp.linkGraphQL(self.instance, self.id, "hello", "hello")
        result = self.gqlApp.run(self.id, "hello")
        self.assertEqual("Hello", result, "None came back")
        
        #Test userId get
        result = self.gqlApp.run(self.id, "getUserId")
        self.assertEqual(self.userId, result, "Wrong result")

        #Test username get
        result = self.gqlApp.run(self.id, "getUsername")
        self.assertEqual(self.username, result, "Wrong result")

        #Test payload get
        result = self.gqlApp.run(self.id, "getPayload")
        self.assertEqual(self.payload, result, "Wrong result")
        
        #Test source get
        result = self.gqlApp.run(self.id, "getSource")
        self.assertEqual(self.source, result, "Wrong result")
    
    def test_instance_action_map(self):
        self.instance = DummyController(userId=self.userId, username=self.username, payload=self.payload, source=self.source)
        #These go to the None parentType
        self.gqlApp.linkGraphQL(self.instance, action=self.id+"hello", func="hello")
        self.gqlApp.linkGraphQL(self.instance, action=self.id+"getUserId", func="getUserId")
        self.gqlApp.linkGraphQL(self.instance, action=self.id+"getUsername", func="getUsername")
        self.gqlApp.linkGraphQL(self.instance, action=self.id+"getPayload", func="getPayload")
        self.gqlApp.linkGraphQL(self.instance, action=self.id+"getSource", func="getSource")

        #Goes to self.id+"source" ParentType
        self.gqlApp.linkGraphQL(self.instance, parentType=self.id+"source", action=self.id+"getSource", func="getSource")

        result = self.gqlApp.run(self.id+"hello", "hello")
        self.assertEqual("Hello", result, "None came back")
        
        #Test userId get
        result = self.gqlApp.run(self.id+"getUserId", "getUserId")
        self.assertEqual(self.userId, result, "Wrong result")

        #Test username get
        result = self.gqlApp.run(self.id+"getUsername", "getUsername")
        self.assertEqual(self.username, result, "Wrong result")

        #Test payload get
        result = self.gqlApp.run(self.id+"getPayload", "getPayload")
        self.assertEqual(self.payload, result, "Wrong result")
        
        #Test source get
        result = self.gqlApp.run(self.id+"getSource", "getSource")
        self.assertEqual(self.source, result, "Wrong result")

        result = self.gqlApp.run(self.id+"source", self.id+"getSource")
        self.assertEqual(self.source, result, "Wrong result")
    
    def test_class_args_kwargs(self):
        self.gqlApp.linkGraphQL(self.controlClass, self.id+"kwargs_args", args=self.args, kwargs=self.kwargs)
        self.gqlApp.linkGraphQL(self.controlClass, self.id+"kwargs", kwargs=self.kwargs)
        self.gqlApp.linkGraphQL(self.controlClass, self.id+"args", args=self.args)
        
        result = self.gqlApp.run(self.id+"kwargs_args", "getKwargsArgs")
        self.assertEqual(self.args, result[0], "Args was not returned")
        self.assertEqual(self.kwargs, result[1], "Kwargs was not returned")
        

        result = self.gqlApp.run(self.id+"kwargs", "getKwargs")
        self.assertEqual(self.kwargs, result, "Kwargs was not returned")
        
        result = self.gqlApp.run(self.id+"args", "getArgs")
        self.assertEqual(self.args, result, "Args was not returned")
    
    def test_instance_args_kwargs(self):
        self.instance = DummyController(userId=self.userId, username=self.username, payload=self.payload, source=self.source)

        self.gqlApp.linkGraphQL(self.instance, self.id+"kwargs_args", args=self.args, kwargs=self.kwargs)
        self.gqlApp.linkGraphQL(self.instance, self.id+"kwargs", kwargs=self.kwargs)
        self.gqlApp.linkGraphQL(self.instance, self.id+"args", args=self.args)
        
        result = self.gqlApp.run(self.id+"kwargs_args", "getKwargsArgs")
        self.assertEqual(self.args, result[0], "Args was not returned")
        self.assertEqual(self.kwargs, result[1], "Kwargs was not returned")
        

        result = self.gqlApp.run(self.id+"kwargs", "getKwargs")
        self.assertEqual(self.kwargs, result, "Kwargs was not returned")
        
        result = self.gqlApp.run(self.id+"args", "getArgs")
        self.assertEqual(self.args, result, "Args was not returned")