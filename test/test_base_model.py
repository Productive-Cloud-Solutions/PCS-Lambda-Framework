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

from pcs.testing.test_creator import TestUser, createEvent, createUser, LambdaTester

from pcs.models.mongoWrapper import MongoWrapper

#Get, delete, replace, 
class BaseModel(MongoWrapper):
    def __init__(self, table) -> None:        
        super().__init__(host="local-db", table=table)
        
class GeneralTest(unittest.TestCase):

    def setUp(self):
        self.model = BaseModel('base-model-test-table')
        self.dummy = BaseModel('dummy-test-table')
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
                "friend": "Terry", #This is used for aggregation.
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


    def tearDown(self) -> None:
        self.model.db.drop_collection(self.model.table)
        self.dummy.db.drop_collection(self.dummy.table)
        return super().tearDown()

    def test_creation(self):
        
        # test Put with No ID
        result = self.model.put(self.obj)
        self.assertIn('id', result, 'Failed to add ID')
        self.assertNotIn('_id', result, 'Failed to remove _id')
        self.assertEqual(isinstance(result['id'], str), True, 'ID is not string')
        self.assertEqual(result['name'], self.obj['name'], 'ID is not string')
        self.assertIn("created", result, "Created was not added to result")
        self.assertIn("modified", result, "Modified was not added to result")  

        # test Create with No ID
        result = self.model.create(self.obj)
        self.assertIn('id', result, 'Failed to add ID')
        self.assertNotIn('_id', result, 'Failed to remove _id')
        self.assertEqual(isinstance(result['id'], str), True, 'ID is not string')
        self.assertEqual(result['name'], self.obj['name'], 'ID is not string')
        self.assertIn("created", result, "Created was not added to result")
        self.assertIn("modified", result, "Modified was not added to result")  


        # test Put with ID
        result = self.model.put(self.objWithId)
        self.assertIn('id', result, 'Failed to add ID')
        self.assertNotIn('_id', result, 'Failed to remove _id')
        self.assertEqual(isinstance(result['id'], str), True, 'ID is not string')
        self.assertEqual(result['name'], self.objWithId['name'], 'ID is not string')
        self.assertIn("created", result, "Created was not added to result")
        self.assertIn("modified", result, "Modified was not added to result")  
        # find inserted object using inserted ID
        dbObj = self.model.get(self.objWithId['id'])
        self.assertEqual(result['id'], dbObj['id'], 'ID is wrong')


        # test Create with ID
        self.objWithId['id'] += '1' # make new ID
        result = self.model.create(self.objWithId)
        self.assertIn('id', result, 'Failed to add ID')
        self.assertNotIn('_id', result, 'Failed to remove _id')
        self.assertEqual(isinstance(result['id'], str), True, 'ID is not string')
        self.assertIn("created", result, "Created was not added to result")
        self.assertIn("modified", result, "Modified was not added to result")  
        # find inserted object using inserted ID
        dbObj = self.model.get(self.objWithId['id'])
        self.assertEqual(result['id'], dbObj['id'], 'ID is wrong')

        # test Put with _id
        result = self.model.put(self.objWith_Id)
        self.assertIn('id', result, 'Failed to add ID')
        self.assertNotIn('_id', result, 'Failed to remove _id')
        self.assertEqual(isinstance(result['id'], str), True, 'ID is not string')
        self.assertEqual(result['name'], self.objWith_Id['name'], 'ID is not string')
        self.assertIn("created", result, "Created was not added to result")
        self.assertIn("modified", result, "Modified was not added to result")  
        # find inserted object using inserted ID
        dbObj = self.model.get(self.objWith_Id['_id'])
        self.assertEqual(result['id'], dbObj['id'], 'ID is wrong')

        # test Create with _id
        self.objWith_Id['_id'] += '1' # make new ID
        result = self.model.create(self.objWith_Id)
        self.assertIn('id', result, 'Failed to add ID')
        self.assertNotIn('_id', result, 'Failed to remove _id')
        self.assertEqual(isinstance(result['id'], str), True, 'ID is not string')
        self.assertIn("created", result, "Created was not added to result")
        self.assertIn("modified", result, "Modified was not added to result")
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
        self.assertIn("created", result, "Created was not added to result")
        self.assertIn("modified", result, "Modified was not added to result")  


        # test create_or_replace() with id
        result = self.model.create_or_replace(self.objWithId)
        self.assertIn('id', result, 'Failed to add ID')
        self.assertNotIn('_id', result, 'Failed to remove _id')
        self.assertEqual(isinstance(result['id'], str), True, 'ID is not string')
        self.assertIn("created", result, "Created was not added to result")
        self.assertIn("modified", result, "Modified was not added to result")  
        # find inserted object using inserted ID
        dbObj = self.model.get(self.objWithId['id'])
        self.assertEqual(result['id'], dbObj['id'], 'ID is wrong')
        self.assertEqual(result['name'], dbObj['name'], 'name not correct')

        # test create_or_replace() with _id
        result = self.model.create_or_replace(self.objWith_Id)
        self.assertIn('id', result, 'Failed to add ID')
        self.assertNotIn('_id', result, 'Failed to remove _id')
        self.assertEqual(isinstance(result['id'], str), True, 'ID is not string')
        self.assertIn("created", result, "Created was not added to result")
        self.assertIn("modified", result, "Modified was not added to result")  
        # find inserted object using inserted ID
        dbObj = self.model.get(self.objWith_Id['id'])
        self.assertEqual(result['id'], dbObj['id'], 'ID is wrong')
        self.assertEqual(result['name'], dbObj['name'], 'name not correct')


        # test create_or_replace() exiting with id
        self.objWithId = self.model.get(self.objWithId['id'])
        self.objWithId['name'] = 'updated name' # make new ID
        result = self.model.create_or_replace(self.objWithId)
        self.assertIn('id', result, 'Failed to add ID')
        self.assertNotIn('_id', result, 'Failed to remove _id')
        self.assertEqual(isinstance(result['id'], str), True, 'ID is not string')
        self.assertIn("modified", result, "Modified was not added to result")
        self.assertIn("created", result, "Created was not added to result")
        # find inserted object using inserted ID
        dbObj = self.model.get(self.objWithId['id'])
        self.assertEqual(result['id'], dbObj['id'], 'ID is wrong')
        self.assertEqual(result['name'], dbObj['name'], 'name not correct')
        self.assertEqual('updated name', dbObj['name'], 'name not correct')


        # test create_or_replace() existing with _id
        self.objWith_Id = self.model.get(self.objWith_Id['id'])
        self.objWith_Id['name'] = 'updated name' # make new ID
        result = self.model.create_or_replace(self.objWith_Id)
        self.assertIn('id', result, 'Failed to add ID')
        self.assertNotIn('_id', result, 'Failed to remove _id')
        self.assertEqual(isinstance(result['id'], str), True, 'ID is not string')
        self.assertIn("modified", result, "Modified was not added to result")
        self.assertIn("created", result, "Created was not added to result")
        # find inserted object using inserted ID
        dbObj = self.model.get(self.objWith_Id['id'])
        self.assertEqual(result['id'], dbObj['id'], 'ID is wrong')
        self.assertEqual(result['name'], dbObj['name'], 'name not correct')
        self.assertEqual('updated name', dbObj['name'], 'name not correct')

   
    def test_update(self):
        # test Update with No ID
        in_result = self.model.put(self.obj)
        self.assertIn('id', in_result, 'Failed to add ID')
        self.assertNotIn('_id', in_result, 'Failed to remove _id')
        self.assertEqual(isinstance(in_result['id'], str), True, 'ID is not string')
        self.assertNotEqual("Jimmy", in_result['name'], 'Name was not updated')
        self.assertIn("modified", in_result, "Modified was not added to in_result")
        self.assertIn("created", in_result, "Created was not added to in_result")
        query = {"$set": {
            "name":"Jimmy"
        }}
        up_result = self.model.update(in_result['id'], query)
        self.assertIn('id', up_result, 'Failed to add ID')
        self.assertNotIn('_id', up_result, 'Failed to remove _id')
        self.assertEqual(isinstance(up_result['id'], str), True, 'ID is not string')
        self.assertEqual("Jimmy", up_result['name'], 'Name was not updated')
        self.assertIn("modified", up_result, "Modified was not added to up_result")
        self.assertNotEqual(in_result['modified'], up_result['modified'], "Modified was not not updated")
        self.assertIn("created", up_result, "Created was not added to up_result")

        # test Update with ID
        in_result = self.model.put(self.objWithId)
        self.assertIn('id', in_result, 'Failed to add ID')
        self.assertNotIn('_id', in_result, 'Failed to remove _id')
        self.assertEqual(isinstance(in_result['id'], str), True, 'ID is not string')
        self.assertNotEqual("Johnson", in_result['name'], 'Name was not updated')
        self.assertIn("modified", in_result, "Modified was not added to in_result")
        self.assertIn("created", in_result, "Created was not added to in_result")
        query = {"$set": {
            "name":"Johnson"
        }}
        up_result = self.model.update(self.objWithId['id'], query)
        self.assertIn('id', up_result, 'Failed to add ID')
        self.assertNotIn('_id', up_result, 'Failed to remove _id')
        self.assertEqual(isinstance(up_result['id'], str), True, 'ID is not string')
        self.assertEqual("Johnson", up_result['name'],'Name was not updated')
        self.assertIn("modified", up_result, "Modified was not added to up_result")
        self.assertNotEqual(in_result['modified'], up_result['modified'], "Modified was not not updated")
        self.assertIn("created", up_result, "Created was not added to up_result")
        # # find inserted object using inserted ID
        # dbObj = self.model.get(self.objWithId['id'])
        # self.assertEqual(result['id'], dbObj['id'], 'ID is wrong')
        

        # test Update with _ID
        in_result = self.model.put(self.objWith_Id)
        self.assertIn('id', in_result, 'Failed to add ID')
        self.assertNotIn('_id', in_result, 'Failed to remove _id')
        self.assertEqual(isinstance(in_result['id'], str), True, 'ID is not string')
        self.assertNotEqual("Jerry", in_result['name'], 'Name was not updated')
        self.assertIn("modified", in_result, "Modified was not added to in_result")
        self.assertIn("created", in_result, "Created was not added to in_result")
        query = {"$set": {
            "name":"Jerry"
        }}
        up_result = self.model.update(self.objWith_Id['_id'], query)
        self.assertIn('id', up_result, 'Failed to add ID')
        self.assertNotIn('_id', up_result, 'Failed to remove _id')
        self.assertEqual(isinstance(up_result['id'], str), True, 'ID is not string')
        self.assertEqual("Jerry", up_result['name'], 'Name was not updated')
        self.assertIn("modified", up_result, "Modified was not added to up_result")
        self.assertNotEqual(in_result['modified'], up_result['modified'], "Modified was not not updated")
        self.assertIn("created", up_result, "Created was not added to up_result")
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

        # for x in list(query.values()):
        #     print(x)

        result = self.model.findMany(query)

        for r in result:
            self.assertIn('id', r, 'Failed to add ID')
            self.assertNotIn('_id', r, 'Failed to remove _id')
            self.assertIn("modified", r, "Modified was not added to r")
            self.assertIn("created", r, "Created was not added to r")
            self.assertEqual(isinstance(r['id'], str), True, 'ID is not string')
            self.assertEqual("Terry", r['name'], 'Name was not updated')

        result = self.model.insertMany(self.objsWithIds[1:])

        query={
            "_id": {
                "$in": result
            }
        }

        result = self.model.findMany(query)
        for r in result:
            self.assertIn('id', r, 'Failed to add ID')
            self.assertNotIn('_id', r, 'Failed to remove _id')
            self.assertIn("modified", r, "Modified was not added to r")
            self.assertIn("created", r, "Created was not added to r")
            self.assertEqual(isinstance(r['id'], str), True, 'ID is not string')
            self.assertEqual("truth", r['universe'], 'Name was not updated')

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
            self.assertIn("modified", r, "Modified was not added to r")
            self.assertIn("created", r, "Created was not added to r")
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
            self.assertIn("modified", r, "Modified was not added to r")
            self.assertIn("created", r, "Created was not added to r")
            self.assertEqual(isinstance(r['id'], str), True, 'ID is not string')
            self.assertEqual("lies", r['universe'], 'Name was not updated')

    def test_delete(self):
        # test Delete with No ID
        result = self.model.put(self.obj)
        self.assertIn('id', result, 'Failed to add ID')
        self.assertNotIn('_id', result, 'Failed to remove _id')
        self.assertEqual(isinstance(result['id'], str), True, 'ID is not string')
        self.assertIn("modified", result, "Modified was not added to r")
        self.assertIn("created", result, "Created was not added to r")
        

        result = self.model.delete(result['id'])
        self.assertIn('id', result, 'Failed to add ID')
        self.assertNotIn('_id', result, 'Failed to remove _id')
        self.assertEqual(isinstance(result['id'], str), True, 'ID is not string')

        # test Delete with ID
        result = self.model.put(self.objWithId)
        self.assertIn('id', result, 'Failed to add ID')
        self.assertNotIn('_id', result, 'Failed to remove _id')
        self.assertEqual(isinstance(result['id'], str), True, 'ID is not string')
        self.assertIn("modified", result, "Modified was not added to r")
        self.assertIn("created", result, "Created was not added to r")

        result = self.model.delete(self.objWithId['id'])
        self.assertIn('id', result, 'Failed to add ID')
        self.assertNotIn('_id', result, 'Failed to remove _id')
        self.assertEqual(isinstance(result['id'], str), True, 'ID is not string')


        # test Delete with _ID
        result = self.model.put(self.objWith_Id)
        self.assertIn('id', result, 'Failed to add ID')
        self.assertNotIn('_id', result, 'Failed to remove _id')
        self.assertEqual(isinstance(result['id'], str), True, 'ID is not string')
        self.assertIn("modified", result, "Modified was not added to r")
        self.assertIn("created", result, "Created was not added to r")

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
            self.assertIn("modified", r, "Modified was not added to r")
            self.assertIn("created", r, "Created was not added to r")

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
        self.assertIn("modified", result, "Modified was not added to r")
        self.assertIn("created", result, "Created was not added to r")

        result = self.model.get(result['id'])
        self.assertIn('id', result, 'Failed to add ID')
        self.assertNotIn('_id', result, 'Failed to remove _id')
        self.assertEqual(isinstance(result['id'], str), True, 'ID is not string')
        self.assertEqual("found it", result['name'], "Found the wrong value")
        self.assertIn("modified", result, "Modified was not added to r")
        self.assertIn("created", result, "Created was not added to r")

        #Single Item Retrieval with find
        query={
            "name":"found it"
        }

        result = self.model.find(query)
        self.assertIn('id', result, 'Failed to add ID')
        self.assertNotIn('_id', result, 'Failed to remove _id')
        self.assertEqual(isinstance(result['id'], str), True, 'ID is not string')
        self.assertEqual("found it", result['name'], "Found the wrong value")
        self.assertIn("modified", result, "Modified was not added to r")
        self.assertIn("created", result, "Created was not added to r")

        #Multiple item retrieval with find
        result = self.model.insertMany(self.objsWithIds)
        result = self.model.findManyByIds(result)
        for r in result:
            self.assertIn('id', r, 'Failed to add ID')
            self.assertNotIn('_id', r, 'Failed to remove _id')
            self.assertEqual(isinstance(r['id'], str), True, 'ID is not string')
            self.assertEqual("truth", r['universe'], 'Name was not updated')
            self.assertIn("modified", r, "Modified was not added to r")
            self.assertIn("created", r, "Created was not added to r")
        
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
            self.assertIn("modified", r, "Modified was not added to r")
            self.assertIn("created", r, "Created was not added to r")

    def test_replace(self):
        # test create_or_replace() exiting with id
        result = self.model.put(self.objWithId)
        self.assertIn('id', result, 'Failed to add ID')
        self.assertNotIn('_id', result, 'Failed to remove _id')
        self.assertEqual(isinstance(result['id'], str), True, 'ID is not string')
        self.assertNotEqual('updated name-'+self.uuid, result['name'], "Wrong name found")
        self.assertIn("modified", result, "Modified was not added to r")
        self.assertIn("created", result, "Created was not added to r")

        self.objWithId = self.model.get(self.objWithId['id'])# get self.objWithId to keep from overwriting created
        self.objWithId['name'] = 'updated name-'+self.uuid # make new ID
        result = self.model.replace(self.objWithId['id'], self.objWithId)
        self.assertIn('id', result, 'Failed to add ID')
        self.assertNotIn('_id', result, 'Failed to remove _id')
        self.assertEqual(isinstance(result['id'], str), True, 'ID is not string')
        self.assertEqual('updated name-'+self.uuid, result['name'], "Wrong name found")
        self.assertIn("modified", result, "Modified was not added to r")
        self.assertIn("created", result, "Created was not added to r")

    def test_find_one_and_update(self):
        #Multiple item retrieval with find
        self.objWithId['name'] = "Timmy-"+self.uuid
        in_result = self.model.put(self.objWithId)
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
        self.assertIn("modified", result, "Modified was not added to r")
        self.assertNotEqual(result["modified"], in_result["modified"], "Modified was not updated")
        self.assertIn("created", result, "Created was not added to r")

    # def test_find_skip_limit(self):
    #     #insert Many
    #     item_list = []
    #     self.obj['name'] = 'Terry'
    #     self.objWith_Id['name'] = 'Terry'
    #     self.objWithId['name'] = 'Terry'

    #     item_list.append(self.obj)
    #     item_list.append(self.objWith_Id)
    #     item_list.append(self.objWithId)

    #     result = self.model.insertMany(item_list)

    #     query={
    #         "_id": {
    #             "$in": result
    #         }
    #     }

    #     result = self.model.findMany(query)

    #     self.assertEqual(len(result), 3, "Skip was processed with a value other than False")
        
    #     result = self.model.findMany(query, skip=1)

    #     self.assertEqual(len(result), 2, "Skip was not processed")

    #     for r in result:
    #         self.assertIn('id', r, 'Failed to add ID')
    #         self.assertNotIn('_id', r, 'Failed to remove _id')
    #         self.assertEqual(isinstance(r['id'], str), True, 'ID is not string')
    #         self.assertEqual("Terry", r['name'], 'Name was not updated')

    #     result = self.model.insertMany(self.objsWithIds[1:])

    # #Testing Aggregate with Base Model
    # def test_aggregate(self):
    #     #add name = Terry to both objwithId and objWith_Id
    #     item_list = []
    #     self.objWith_Id['name'] = 'Terry'
    #     self.objWithId['name'] = 'Terry'

    #     #Add objWithId and objWith_Id to item_list
    #     item_list.append(self.objWith_Id)
    #     item_list.append(self.objWithId)

    #     #Insert Objects into model with name terry
    #     result = self.model.insertMany(item_list)
        
    #     query={
    #         "_id": {
    #             "$in": result
    #         }
    #     }

    #     result = self.model.findMany(query)

    #     for r in result:
    #         self.assertIn('id', r, 'Failed to add ID')
    #         self.assertNotIn('_id', r, 'Failed to remove _id')
    #         self.assertEqual(isinstance(r['id'], str), True, 'ID is not string')
    #         self.assertEqual("Terry", r['name'], 'Name was not updated')

    #     #Insert Objs with Ids into dummy(BaseModel) with the friend = Terry
    #     result = self.dummy.insertMany(self.objsWithIds[1:])
        
    #     query={
    #         "_id": {
    #             "$in": result
    #         }
    #     }

    #     result = self.dummy.findMany(query)

    #     for r in result:
    #         self.assertIn('id', r, 'Failed to add ID')
    #         self.assertNotIn('_id', r, 'Failed to remove _id')
    #         self.assertEqual(isinstance(r['id'], str), True, 'ID is not string')
    #         self.assertEqual("Terry", r['friend'], 'Name was not updated')
        
    #     #Set query for aggregate
    #     query = {
    #         "_id" : self.objWithId["_id"] #got changed by insert many. Id does not exist
    #     }

    #     """
    #     Using the name field from self.model and friend field from self.dummy
    #     if they are equal return it from aggregation under the name self.dummy.table
    #     query is used for matching to the self.objWithId (This is the main result,
    #     aggregation is added to it under self.dummy.table in r)
    #     """
    #     result = self.model.aggregate(query, self.dummy, "name", "friend")
        
    #     for r in result:
    #         self.assertIn("id", r, "Failed to add Id")
    #         self.assertEqual(self.objWithId["_id"], r['id'], "Ids are not the same")
    #         for d in r[self.dummy.table]:
    #             self.assertEqual(r['name'], d['friend'])
        
    #     query = {
    #         "_id" : self.objWith_Id["_id"]
    #     }

    #     """
    #     Same as above but use self.objWith_Id this time(This is the main result,
    #     aggregation is added to it under self.dummy.table in r)
    #     """
    #     result = self.model.aggregate(query, self.dummy, "name", "friend")
        
    #     for r in result:
    #         self.assertIn("id", r, "Failed to add Id")
    #         self.assertEqual(self.objWith_Id["_id"], r['id'], "Ids are not the same")
    #         for d in r[self.dummy.table]:
    #             self.assertEqual(r['name'], d['friend'])
        
    #     query = {
    #         "_id" : self.objWith_Id["_id"]
    #     }

    #     """
    #     Same as above but use self.objWith_Id this time(This is the main result,
    #     aggregation is added to it under self.dummy.table in r)
    #     convertIds = False, so the r should have an _id not id
    #     """
    #     result = self.model.aggregate(query, self.dummy, "name", "friend", convertIds=False)
        
    #     for r in result:
    #         self.assertIn("_id", r, "Failed to add Id")
    #         self.assertEqual(self.objWith_Id["_id"], r['_id'], "Ids are not the same")
    #         for d in r[self.dummy.table]:
    #             self.assertEqual(r['name'], d['friend'])

    # def test_errors(self):
    #     pass
       
