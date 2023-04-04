# test for notes API
import os
import app
import uuid
import boto3
import unittest
import time
import random
from datetime import datetime
from unittest.mock import patch, MagicMock, Mock

from util.test_creator import TestUser, createEvent, LambdaTester
from util.test_functions import loadSample

tester = LambdaTester(app.lambda_handler)

class GeneralTest(unittest.TestCase):

    def setUp(self):
        self.socialRecord = loadSample("sample_social.json")


    
    @patch('pyairtable.api.abstract.ApiAbstract._request')
    def test_socials(self, mock_social:MagicMock):
        #Current year exists in query
        mock_social.return_value = {"Records" : [self.socialRecord]} 
        result = tester.createEvent("getSocials")

        self.assertIn("instagram", result, "The current year is not correct")
        self.assertIn("twitter", result, "The current year is not correct")
        self.assertIn("facebook", result, "The current year is not correct")
        self.assertIn("linkedin", result, "The current year is not correct")
        
        mock_social.return_value = {"Records" : ""}
        result = tester.createEvent("getSocials")

        self.assertEqual(result['instagram'], "", "No value should be passed")
        self.assertEqual(result['twitter'], "", "No value should be passed")
        self.assertEqual(result['facebook'], "", "No value should be passed")
        self.assertEqual(result['linkedin'], "", "No value should be passed")