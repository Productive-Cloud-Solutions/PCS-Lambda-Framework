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

from pcs.testing.test_creator import TestUser, createEvent, LambdaTester, loadSample

from pcs.util.airTable import retry, Table
from pcs.models.airTableCache import AirTableCache

cache_model = AirTableCache()


tester = LambdaTester(app.lambda_handler)



class GeneralTest(unittest.TestCase):

    def setUp(self):
        self.count = 0
        self.API_LIMIT = 1.0 / 5
        self.id = str(uuid.uuid4())
        pass
        # patcher = patch('__builtin__.sum', return_value=99)
        # self.mock_sum = patcher.start()
        # self.addCleanup(patcher.stop)
        # patcher = patch('pyairtable.Table')
        # self.mockBaseTable = patcher.start()
        # self.addCleanup(patcher.stop)
        # patch('util.airTable.airBase')
    

    def test_decurator(self):
        pass

    # from pyairtable import Table as airTable
    # from pyairtable import Base as airBase
    # @patch('util.airTable.Table')
    def test_one_retry(self):
        @retry()
        def a():
            self.count += 1
            return "expected_result"
        
        self.assertEqual(a(), "expected_result")
        self.assertEqual(self.count, 1, 'Wrong number of retires')

    @patch('pcs.util.airTable.time')
    def test_retry_wrong_error(self, timeMock:MagicMock):
        @retry()
        def a():
            self.count += 1
            raise Exception('Boom!!!')
        
        with self.assertRaises(Exception) as error:
            self.assertEqual(a(), "expected_result")
        self.assertEqual(self.count, 1, 'Wrong number of retires')
        timeMock.sleep.assert_not_called()
        self.assertEqual("Boom!!!", str(error.exception), 'Wrong number of retires')

    @patch('pcs.util.airTable.time')
    def test_retry_correct_error(self, timeMock:MagicMock):
        @retry(5)
        def a():
            self.count += 1
            raise Exception("('429 Client Error: Too Many Requests for url: https:'")
        
        with self.assertRaises(Exception) as error:
            self.assertEqual(a(), "expected_result")
        self.assertEqual(self.count, 5, 'Wrong number of retires')
        timeMock.sleep.assert_any_call(self.API_LIMIT)
        timeMock.sleep.assert_any_call(self.API_LIMIT + (self.API_LIMIT/2))
        timeMock.sleep.assert_any_call(self.API_LIMIT + ((self.API_LIMIT/2)*3))
        
        self.count = 0 
        @retry(2)
        def a():
            self.count += 1
            raise Exception("('429 Client Error: Too Many Requests for url: https:'")
        
        with self.assertRaises(Exception) as error:
            self.assertEqual(a(), "expected_result")
        self.assertEqual(self.count, 2, 'Wrong number of retires')
        timeMock.sleep.assert_any_call(self.API_LIMIT)
        timeMock.sleep.assert_any_call(self.API_LIMIT + (self.API_LIMIT/2))
        
     

   
    def test_airtable_cache(self):

        value = str(uuid.uuid4())

        # no cache
        cacheVal = cache_model.getCache(self.id)
        self.assertEqual(cacheVal, None, 'Wrong Cache Value')
      
        # cache set and get
        cache_model.setCache(self.id, value)
        cacheVal = cache_model.getCache(self.id)
        self.assertEqual(cacheVal, value, 'Wrong Cache Value')


        # cache expire
        with patch('pcs.models.airTableCache.time.time') as mockTime:
            mockTime.return_value = 0
            cache_model.setCache(self.id, value)
        cacheVal = cache_model.getCache(self.id)
        self.assertEqual(cacheVal, None, 'Wrong Cache Value')

    # @patch('util.airTable.airTable')
    @patch('pcs.util.airTable.airTableCache_model')
    def test_function_caching(self, mockDb:MagicMock):
        mockDb.getCache.return_value = None

        
        




    def test_delete(self):
        pass



    def test_retrieval(self):
        pass 
        # get notes | no notes
        # source = {
        #     'id':self.pusleID
        # }
        # result = tester.createEvent("notes", parentType="PulseInstance", user=self.instructor, 
        #     source = source)
        # self.assertEqual(result, [], 'Wrong len')

        # create note about a participant 1 pulse 1
        # createdNoteText = str(uuid.uuid4())
        # payload = {}
        # payload['text'] = createdNoteText
        # payload['userId'] = self.user.id
        # payload['type'] = 'public'
        # payload['recordType'] = 'pulse'
        # payload['recordId'] = self.pusleID
        # result = tester.createEvent("createNote", user=self.instructor, payload = payload,
        #     _id=self.id+'note')
        # self.assertEqual(result['text'], payload['text'], 'Wrong text')
        # self.assertEqual(result['type'], 'public' , 'Wrong type')


        # # get notes after first note
        # source = {
        #     'id':self.pusleID
        # }
        # result = tester.createEvent("notes", parentType="PulseInstance", user=self.instructor, 
        #     source = source)
        # self.assertEqual(len(result), 1, 'Wrong text')
        # self.assertEqual(result[0]['text'], createdNoteText, 'Wrong text')
        # self.assertEqual(result[0]['type'], 'public' , 'Wrong type')

        # # create note about a participant 2 pulse 1
        # createdNoteText2 = str(uuid.uuid4())
        # payload = {}
        # payload['text'] = createdNoteText2
        # payload['userId'] = self.user2.id
        # payload['type'] = 'private'
        # payload['recordType'] = 'pulse'
        # payload['recordId'] = self.pusleID
        # result = tester.createEvent("createNote", user=self.instructor, payload = payload,
        #     _id=self.id+'note2')
        # self.assertEqual(result['text'], payload['text'], 'Wrong text')
        # self.assertEqual(result['type'], 'private' , 'Wrong type')

        # # get notes after second note
        # source = {
        #     'id':self.pusleID
        # }
        # result = tester.createEvent("notes", parentType="PulseInstance", user=self.instructor, 
        #     source = source)
        # self.assertEqual(len(result), 2, 'Wrong text')
        # self.assertEqual(result[0]['text'], createdNoteText, 'Wrong text')
        # self.assertEqual(result[0]['type'], 'public' , 'Wrong type')


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


