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

from pcs.testing.test_creator import TestUser, LambdaTester

from pcs.models.baseModel import BaseModel


class GeneralTest(unittest.TestCase):

    def setUp(self):
        self.model = BaseModel('base-model-test-table')
        self.objs = []
        self.objsWithIds = []
        self.uuid = str(uuid.uuid4())

        for i in range(10):
            self.objs.append({
                'name':str(uuid.uuid4()),
                'value':str(uuid.uuid4()),
                'prop':str(uuid.uuid4()),
                'count': i
            })

        for i in range(10):
            self.objsWithIds.append({
                'id':str(uuid.uuid4()),
                'name':str(uuid.uuid4()),
                'value':str(uuid.uuid4()),
                'prop':str(uuid.uuid4()),
                'count': i,
                "universe": "truth",
                "connection": self.uuid
            })
        
        self.obj = self.objs[0]
        self.objWithId = self.objsWithIds[0]

        self.objWith_Id = {
                '_id':str(uuid.uuid4()),
                'name':str(uuid.uuid4()),
                'value':str(uuid.uuid4()),
                'prop':str(uuid.uuid4())
        }


    def test_creation(self):
        
        # test Put with No ID
        result = self.model.put(self.obj)
        self.assertIn('id', result, 'Failed to add ID')
        self.assertNotIn('_id', result, 'Failed to remove _id')
        self.assertEqual(isinstance(result['id'], str), True, 'ID is not string')
        self.assertEqual(result['name'], self.obj['name'], 'ID is not string')

        # test Create with No ID
        result = self.model.create(self.obj)
        self.assertIn('id', result, 'Failed to add ID')
        self.assertNotIn('_id', result, 'Failed to remove _id')
        self.assertEqual(isinstance(result['id'], str), True, 'ID is not string')
        self.assertEqual(result['name'], self.obj['name'], 'ID is not string')


        # test Put with ID
        result = self.model.put(self.objWithId)
        self.assertIn('id', result, 'Failed to add ID')
        self.assertNotIn('_id', result, 'Failed to remove _id')
        self.assertEqual(isinstance(result['id'], str), True, 'ID is not string')
        self.assertEqual(result['name'], self.objWithId['name'], 'ID is not string')
        # find inserted object using inserted ID
        dbObj = self.model.get(self.objWithId['id'])
        self.assertEqual(result['id'], dbObj['id'], 'ID is wrong')


        # test Create with ID
        self.objWithId['id'] += '1' # make new ID
        result = self.model.create(self.objWithId)
        self.assertIn('id', result, 'Failed to add ID')
        self.assertNotIn('_id', result, 'Failed to remove _id')
        self.assertEqual(isinstance(result['id'], str), True, 'ID is not string')
        # find inserted object using inserted ID
        dbObj = self.model.get(self.objWithId['id'])
        self.assertEqual(result['id'], dbObj['id'], 'ID is wrong')

        # test Put with _id
        result = self.model.put(self.objWith_Id)
        self.assertIn('id', result, 'Failed to add ID')
        self.assertNotIn('_id', result, 'Failed to remove _id')
        self.assertEqual(isinstance(result['id'], str), True, 'ID is not string')
        self.assertEqual(result['name'], self.objWith_Id['name'], 'ID is not string')
        # find inserted object using inserted ID
        dbObj = self.model.get(self.objWith_Id['_id'])
        self.assertEqual(result['id'], dbObj['id'], 'ID is wrong')

        # test Create with _id
        self.objWith_Id['_id'] += '1' # make new ID
        result = self.model.create(self.objWith_Id)
        self.assertIn('id', result, 'Failed to add ID')
        self.assertNotIn('_id', result, 'Failed to remove _id')
        self.assertEqual(isinstance(result['id'], str), True, 'ID is not string')
        # find inserted object using inserted ID
        dbObj = self.model.get(self.objWith_Id['_id'])
        self.assertEqual(result['id'], dbObj['id'], 'ID is wrong')

    def test_creation_or_replace(self):

        # test create_or_replace() with No ID
        result = self.model.create_or_replace(self.obj)
        self.assertIn('id', result, 'Failed to add ID')
        self.assertNotIn('id', self.obj, 'Failed ID in object')
        self.assertNotIn('_id', self.obj, 'Failed ID in object')
        self.assertNotIn('_id', result, 'Failed to remove _id')
        self.assertEqual(isinstance(result['id'], str), True, 'ID is not string')
        self.assertEqual(result['name'], self.obj['name'], 'name not correct')


        # test create_or_replace() with id
        result = self.model.create_or_replace(self.objWithId)
        self.assertIn('id', result, 'Failed to add ID')
        self.assertNotIn('_id', result, 'Failed to remove _id')
        self.assertEqual(isinstance(result['id'], str), True, 'ID is not string')
        # find inserted object using inserted ID
        dbObj = self.model.get(self.objWithId['id'])
        self.assertEqual(result['id'], dbObj['id'], 'ID is wrong')
        self.assertEqual(result['name'], dbObj['name'], 'name not correct')

        # test create_or_replace() with _id
        result = self.model.create_or_replace(self.objWith_Id)
        self.assertIn('id', result, 'Failed to add ID')
        self.assertNotIn('_id', result, 'Failed to remove _id')
        self.assertEqual(isinstance(result['id'], str), True, 'ID is not string')
        # find inserted object using inserted ID
        dbObj = self.model.get(self.objWith_Id['id'])
        self.assertEqual(result['id'], dbObj['id'], 'ID is wrong')
        self.assertEqual(result['name'], dbObj['name'], 'name not correct')


        # test create_or_replace() exiting with id
        self.objWithId['name'] = 'updated name' # make new ID
        result = self.model.create_or_replace(self.objWithId)
        self.assertIn('id', result, 'Failed to add ID')
        self.assertNotIn('_id', result, 'Failed to remove _id')
        self.assertEqual(isinstance(result['id'], str), True, 'ID is not string')
        # find inserted object using inserted ID
        dbObj = self.model.get(self.objWithId['id'])
        self.assertEqual(result['id'], dbObj['id'], 'ID is wrong')
        self.assertEqual(result['name'], dbObj['name'], 'name not correct')
        self.assertEqual('updated name', dbObj['name'], 'name not correct')


        # test create_or_replace() existing with _id
        self.objWith_Id['name'] = 'updated name' # make new ID
        result = self.model.create_or_replace(self.objWith_Id)
        self.assertIn('id', result, 'Failed to add ID')
        self.assertNotIn('_id', result, 'Failed to remove _id')
        self.assertEqual(isinstance(result['id'], str), True, 'ID is not string')
        # find inserted object using inserted ID
        dbObj = self.model.get(self.objWith_Id['id'])
        self.assertEqual(result['id'], dbObj['id'], 'ID is wrong')
        self.assertEqual(result['name'], dbObj['name'], 'name not correct')
        self.assertEqual('updated name', dbObj['name'], 'name not correct')

   
    def test_update(self):
        # test Update with No ID
        result = self.model.put(self.obj)
        self.assertIn('id', result, 'Failed to add ID')
        self.assertNotIn('_id', result, 'Failed to remove _id')
        self.assertEqual(isinstance(result['id'], str), True, 'ID is not string')
        self.assertNotEqual("Jimmy", result['name'], 'Name was not updated')
        query = {"$set": {
            "name":"Jimmy"
        }}
        result = self.model.update(result['id'], query)
        self.assertIn('id', result, 'Failed to add ID')
        self.assertNotIn('_id', result, 'Failed to remove _id')
        self.assertEqual(isinstance(result['id'], str), True, 'ID is not string')
        self.assertEqual("Jimmy", result['name'], 'Name was not updated')

        # test Update with ID
        result = self.model.put(self.objWithId)
        self.assertIn('id', result, 'Failed to add ID')
        self.assertNotIn('_id', result, 'Failed to remove _id')
        self.assertEqual(isinstance(result['id'], str), True, 'ID is not string')
        self.assertNotEqual("Johnson", result['name'], 'Name was not updated')
        query = {"$set": {
            "name":"Johnson"
        }}
        result = self.model.update(self.objWithId['id'], query)
        self.assertIn('id', result, 'Failed to add ID')
        self.assertNotIn('_id', result, 'Failed to remove _id')
        self.assertEqual(isinstance(result['id'], str), True, 'ID is not string')
        self.assertEqual("Johnson", result['name'],'Name was not updated')
        # # find inserted object using inserted ID
        # dbObj = self.model.get(self.objWithId['id'])
        # self.assertEqual(result['id'], dbObj['id'], 'ID is wrong')
        

        # test Update with _ID
        result = self.model.put(self.objWith_Id)
        self.assertIn('id', result, 'Failed to add ID')
        self.assertNotIn('_id', result, 'Failed to remove _id')
        self.assertEqual(isinstance(result['id'], str), True, 'ID is not string')
        self.assertNotEqual("Jerry", result['name'], 'Name was not updated')
        query = {"$set": {
            "name":"Jerry"
        }}
        result = self.model.update(self.objWith_Id['_id'], query)
        self.assertIn('id', result, 'Failed to add ID')
        self.assertNotIn('_id', result, 'Failed to remove _id')
        self.assertEqual(isinstance(result['id'], str), True, 'ID is not string')
        self.assertEqual("Jerry", result['name'], 'Name was not updated')
        # # find inserted object using inserted ID
        # dbObj = self.model.get(self.objWith_Id['id'])
        # self.assertEqual(result['id'], dbObj['id'], 'ID is wrong')

    def test_insert_many(self):
        #Update Many
        item_list = []
        self.obj['name'] = 'Terry'
        self.objWith_Id['name'] = 'Terry'
        self.objWithId['name'] = 'Terry'

        item_list.append(self.obj)
        item_list.append(self.objWith_Id)
        item_list.append(self.objWithId)

        result = self.model.insertMany(item_list)

        query={
            "_id": {
                "$in": result
            }
        }

        result = self.model.findMany(query)
        for r in result:
            self.assertIn('id', result, 'Failed to add ID')
            self.assertNotIn('_id', result, 'Failed to remove _id')
            self.assertEqual(isinstance(result['id'], str), True, 'ID is not string')
            self.assertEqual("Terry", result['name'], 'Name was not updated')

        result = self.model.insertMany(self.objsWithIds[1:])

        query={
            "_id": {
                "$in": result
            }
        }

        result = self.model.findMany(query)
        for r in result:
            self.assertIn('id', result, 'Failed to add ID')
            self.assertNotIn('_id', result, 'Failed to remove _id')
            self.assertEqual(isinstance(result['id'], str), True, 'ID is not string')
            self.assertEqual("truth", result['universe'], 'Name was not updated')

    def test_update_many(self):
        #Testing by finding a value in object
        query={
            "name":"Terry"
        }

        newval = {"$set": {
            "name":"Barry"
        }}

        result = self.model.updateMany(query, newval)
        query={
            "_id": {
                "$in": result
            }
        }

        result = self.model.findMany(query)
        for r in result:
            self.assertIn('id', r, 'Failed to add ID')
            self.assertNotIn('_id', r, 'Failed to remove _id')
            self.assertEqual(isinstance(r['id'], str), True, 'ID is not string')
            self.assertEqual("Barry", r['name'], 'Name was not updated')

        #Testing update many with objsWithIds
        query={
            "universe":"truth"
        }

        newval = {"$set": {
            "universe":"lies"
        }}

        result = self.model.updateMany(query, newval)

        result = self.model.findManyByIds(result)
        for r in result:
            self.assertIn('id', r, 'Failed to add ID')
            self.assertNotIn('_id', r, 'Failed to remove _id')
            self.assertEqual(isinstance(r['id'], str), True, 'ID is not string')
            self.assertEqual("lies", r['universe'], 'Name was not updated')

    def test_delete(self):
        # test Delete with No ID
        result = self.model.put(self.obj)
        self.assertIn('id', result, 'Failed to add ID')
        self.assertNotIn('_id', result, 'Failed to remove _id')
        self.assertEqual(isinstance(result['id'], str), True, 'ID is not string')

        result = self.model.delete(result['id'])
        self.assertIn('id', result, 'Failed to add ID')
        self.assertNotIn('_id', result, 'Failed to remove _id')
        self.assertEqual(isinstance(result['id'], str), True, 'ID is not string')

        # test Delete with ID
        result = self.model.put(self.objWithId)
        self.assertIn('id', result, 'Failed to add ID')
        self.assertNotIn('_id', result, 'Failed to remove _id')
        self.assertEqual(isinstance(result['id'], str), True, 'ID is not string')

        result = self.model.delete(self.objWithId['id'])
        self.assertIn('id', result, 'Failed to add ID')
        self.assertNotIn('_id', result, 'Failed to remove _id')
        self.assertEqual(isinstance(result['id'], str), True, 'ID is not string')


        # test Delete with _ID
        result = self.model.put(self.objWith_Id)
        self.assertIn('id', result, 'Failed to add ID')
        self.assertNotIn('_id', result, 'Failed to remove _id')
        self.assertEqual(isinstance(result['id'], str), True, 'ID is not string')

        result = self.model.delete(self.objWith_Id['_id'])
        self.assertIn('id', result, 'Failed to add ID')
        self.assertNotIn('_id', result, 'Failed to remove _id')
        self.assertEqual(isinstance(result['id'], str), True, 'ID is not string')


    def test_delete_many(self):
        #Testing update many with objsWithIds
        result = self.model.insertMany(self.objsWithIds)
        result = self.model.findManyByIds(result)
        for r in result:
            self.assertIn('id', r, 'Failed to add ID')
            self.assertNotIn('_id', r, 'Failed to remove _id')
            self.assertEqual(isinstance(r['id'], str), True, 'ID is not string')
            self.assertEqual("truth", r['universe'], 'Name was not updated')

        query = {
            "universe": "truth"
        }

        result = self.model.deleteMany(query)

        result = self.model.findManyByIds(result)
        self.assertEqual([], result, "Something was found")


    def test_retrieval(self):
        #Single Item Retrieval with get
        # test Delete with No ID
        self.obj['name'] = "found it"
        result = self.model.put(self.obj)
        self.assertIn('id', result, 'Failed to add ID')
        self.assertNotIn('_id', result, 'Failed to remove _id')
        self.assertEqual(isinstance(result['id'], str), True, 'ID is not string')

        result = self.model.get(result['id'])
        self.assertIn('id', result, 'Failed to add ID')
        self.assertNotIn('_id', result, 'Failed to remove _id')
        self.assertEqual(isinstance(result['id'], str), True, 'ID is not string')
        self.assertEqual("found it", result['name'], "Found the wrong value")

        #Single Item Retrieval with find
        query={
            "name":"found it"
        }

        result = self.model.find(query)
        self.assertIn('id', result, 'Failed to add ID')
        self.assertNotIn('_id', result, 'Failed to remove _id')
        self.assertEqual(isinstance(result['id'], str), True, 'ID is not string')
        self.assertEqual("found it", result['name'], "Found the wrong value")

        #Multiple item retrieval with find
        result = self.model.insertMany(self.objsWithIds)
        result = self.model.findManyByIds(result)
        for r in result:
            self.assertIn('id', r, 'Failed to add ID')
            self.assertNotIn('_id', r, 'Failed to remove _id')
            self.assertEqual(isinstance(r['id'], str), True, 'ID is not string')
            self.assertEqual("truth", r['universe'], 'Name was not updated')
        
        #Multiple items retrieval with getMany
        query={
            "connection": self.uuid
        }
        result = self.model.getMany(query)
        for r in result:
            self.assertIn('id', r, 'Failed to add ID')
            self.assertNotIn('_id', r, 'Failed to remove _id')
            self.assertEqual(isinstance(r['id'], str), True, 'ID is not string')
            self.assertEqual("truth", r['universe'], 'Name was not updated')

    def test_replace(self):
        # test create_or_replace() exiting with id
        result = self.model.put(self.objWithId)
        self.assertIn('id', result, 'Failed to add ID')
        self.assertNotIn('_id', result, 'Failed to remove _id')
        self.assertEqual(isinstance(result['id'], str), True, 'ID is not string')
        self.assertNotEqual('updated name-'+self.uuid, result['name'], "Wrong name found")

        self.objWithId['name'] = 'updated name-'+self.uuid # make new ID
        result = self.model.replace(self.objWithId['id'], self.objWithId)
        self.assertIn('id', result, 'Failed to add ID')
        self.assertNotIn('_id', result, 'Failed to remove _id')
        self.assertEqual(isinstance(result['id'], str), True, 'ID is not string')
        self.assertEqual('updated name-'+self.uuid, result['name'], "Wrong name found")

    def test_find_one_and_update(self):
        #Multiple item retrieval with find
        self.objWithId['name'] = "Timmy-"+self.uuid
        result = self.model.put(self.objWithId)
        query={
            "name": "Timmy-"+self.uuid
        }
        
        newval={
            "$set":{
                "name": "A Pimp Named Slickback"
            }
        }

        result = self.model.find_one_and_update(query, newval)
        self.assertIn('id', result, 'Failed to add ID')
        self.assertNotIn('_id', result, 'Failed to remove _id')
        self.assertEqual(isinstance(result['id'], str), True, 'ID is not string')
        self.assertEqual("A Pimp Named Slickback", result['name'], 'Name was not updated')

    def test_errors(self):
        pass
       

    @patch('pcs.util.appFileManager.create_presigned_url')
    def test_with_patch(self, patch_s3_generate_url):
        pass

        # # stubbing s3 mocked service function for testing
        # patch_s3_generate_url.return_value = 'https://s3.amazonaws.com/app-bucket/test/obj.jpg'


