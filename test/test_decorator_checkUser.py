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

from pcs.testing.test_creator import TestUser, createEvent, createUser, LambdaTester, loadSample

from pcs.decorators.checkUser import check_user

tester = LambdaTester(app.lambda_handler)



class GeneralTest(unittest.TestCase):

    def setUp(self):
        self.adminUser = createUser(TestUser(type="admin"))
        self.generalUser = createUser(TestUser(type="general"))
        self.managerUser = createUser(TestUser(type="manager"))

    def test_check_user(self):
        @check_user(['admin', 'manager'])
        def a(user, data):
            self.assertIn(user['id'], [self.adminUser.id, self.managerUser.id], "Wrong User Type passed")
            return "expected_result"
        
        self.assertEqual(a(self.adminUser.id, None), "expected_result")
        self.assertEqual(a(self.managerUser.id, None), "expected_result")

        
        @check_user(['general'])
        def b(user, data):
            self.assertIn(user['id'], [self.generalUser.id], "Wrong User Type passed")
            return "was not an admin or manager"
        
        self.assertEqual(b(self.generalUser.id, None), "was not an admin or manager")
        

        @check_user("admin")
        def c(user, data):
            self.assertIn(user['id'], [self.adminUser.id], "Wrong User Type passed")
            return "expected result"
        
        self.assertEqual(c(self.adminUser.id, None), "expected result")
        
        with self.assertRaises(Exception) as error:
            result = a(self.generalUser.id, None)
        self.assertIn("Invalid Permissions", error.exception.args[0], "User has permissions!!!")
        
        with self.assertRaises(Exception) as error:
            result = a("kdsgawehgoewihgsohgaweiohgxghaoi", None)
        self.assertIn("User Account could not be found", error.exception.args[0], "User was found??!!!")

    # @patch('util.airTable.time')
    # def test_retry_wrong_error(self, timeMock:MagicMock):
    #     @retry()
    #     def a():
    #         self.count += 1
    #         raise Exception('Boom!!!')
        
    #     with self.assertRaises(Exception) as error:
    #         self.assertEqual(a(), "expected_result")
    #     self.assertEqual(self.count, 1, 'Wrong number of retires')
    #     timeMock.sleep.assert_not_called()
    #     self.assertEqual("Boom!!!", str(error.exception), 'Wrong number of retires')

    # @patch('util.airTable.time')
    # def test_retry_correct_error(self, timeMock:MagicMock):
    #     @retry(5)
    #     def a():
    #         self.count += 1
    #         raise Exception("('429 Client Error: Too Many Requests for url: https:'")
        
    #     with self.assertRaises(Exception) as error:
    #         self.assertEqual(a(), "expected_result")
    #     self.assertEqual(self.count, 5, 'Wrong number of retires')
    #     timeMock.sleep.assert_any_call(self.API_LIMIT)
    #     timeMock.sleep.assert_any_call(self.API_LIMIT + (self.API_LIMIT/2))
    #     timeMock.sleep.assert_any_call(self.API_LIMIT + ((self.API_LIMIT/2)*3))
        
    #     self.count = 0 
    #     @retry(2)
    #     def a():
    #         self.count += 1
    #         raise Exception("('429 Client Error: Too Many Requests for url: https:'")
        
    #     with self.assertRaises(Exception) as error:
    #         self.assertEqual(a(), "expected_result")
    #     self.assertEqual(self.count, 2, 'Wrong number of retires')
    #     timeMock.sleep.assert_any_call(self.API_LIMIT)
    #     timeMock.sleep.assert_any_call(self.API_LIMIT + (self.API_LIMIT/2))

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


