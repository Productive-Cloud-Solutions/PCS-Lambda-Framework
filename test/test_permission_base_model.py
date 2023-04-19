# test for notes API
import os
import app
import uuid
import boto3
import unittest
import time
import random
import hashlib
from datetime import datetime
from unittest.mock import patch, MagicMock, Mock
from pymongo import MongoClient
# from pymongo.collection import Collection

from pcs.testing.test_creator import TestUser, createEvent, createUser, LambdaTester

from pcs.models.baseModel import BaseModel, PermissionsModel

class GeneralTest(unittest.TestCase):

    def indexHash(self, indexDict):
        if indexDict and isinstance(indexDict, dict):
            return hashlib.md5(str({key:indexDict[key] for key in sorted(indexDict)}).encode()).hexdigest()
        return False

    def setUp(self):
        #Used for testing table creation
        self.id = str(uuid.uuid4())

        self.model = PermissionsModel('test-table')
        self.temp_model = PermissionsModel(self.id+"-permissions")

        #Create users for testing permissions
        self.user = TestUser(type="general").createUser()
        self.adminUser = TestUser(type="admin").createUser()
        self.managerUser = TestUser(type="manager").createUser()

    
    def tearDown(self) -> None:
        self.model.db.drop_collection(self.model.table)
        self.model.db.drop_collection(self.id)
        self.temp_model.db.drop_collection(self.temp_model.table)
        self.temp_model.db.drop_collection(self.id)
        return super().tearDown()
    
    def test_table_creation(self):
        # self.temp_model = PermissionsModel(self.id)
        self.temp_model.db.create_collection(self.id)
        self.temp_model.updateIndexes()

        self.assertEqual(4, len(list(self.temp_model.db[self.temp_model.table].list_indexes())), "Wrong Number of Indexes passed")
        self.assertEqual(1, len(list(self.temp_model.db[self.id].list_indexes())), "Wrong Number of Indexes passed")
        
        self.temp_model.updateIndexes()

        self.assertEqual(False, self.temp_model.check_for_or_create_index({'objectId':1,'userId':1}, unique=True), "Should not have been True")
        self.assertEqual(False, self.temp_model.check_for_or_create_index({'userId':1}, unique=False), "Should not have been True")
        self.assertEqual(False, self.temp_model.check_for_or_create_index({'objectId':1}, unique=False), "Should not have been True")

        self.temp_model.db.drop_collection(self.temp_model.table)
        self.temp_model.db.drop_collection(self.id)

    def test_create_index_with_no_table(self):
        # self.temp_model = PermissionsModel(self.id)
        self.temp_model.updateIndexes()

        self.temp_model.db.drop_collection(self.id)
        

    """
    Override updateIndex in permissions base model
    """    
    # @patch('pymongo.collection.Collection.create_index')
    def test_index_options(self):
        self.temp_model.db.create_collection(self.id)
        self.temp_model.collection_indexes = [
            {
                "index":{'testId':1, "userId":1},
                "options": {"unique":True}
            },
            {
                "index":{'testId':1},
                "options": {"unique":True}
            },
            {
                "index":{'userId':1},
                "options": {"unique":False}
            }
        ]

        col_index = self.temp_model.collection_indexes[2]
        
        with patch('pymongo.collection.Collection.create_index') as mock_collect:
            self.temp_model.updateIndexes()
            index = []
            for k,v in col_index['index'].items():
                index.append((k,v))

            self.assertEqual(3, mock_collect.call_count, "Wrong number of calls")
            mock_collect.assert_called_with(index, name=self.indexHash(col_index["index"]),**col_index['options']) #Need name to assert called with

        self.temp_model.updateIndexes()

        # This does not work with create_index being patched, so no indexes are created
        self.assertEqual(4, len(list(self.temp_model.db[self.temp_model.table].list_indexes())), "Wrong Number of Indexes passed")
        self.assertEqual(1, len(list(self.temp_model.db[self.id].list_indexes())), "Wrong Number of Indexes passed")
        
        self.assertEqual(False, self.temp_model.check_for_or_create_index({'testId':1, "userId":1}, unique=True), "Should not have been True")
        self.assertEqual(False, self.temp_model.check_for_or_create_index({'testId':1}, unique=False), "Should not have been True")
        self.assertEqual(False, self.temp_model.check_for_or_create_index({"userId":1}, unique=False), "Should not have been True")

        self.temp_model.db.drop_collection(self.temp_model.table)
        self.temp_model.db.drop_collection(self.id)
    
    def test_item_creation(self):
        #general user
        result = self.model.getPermission(self.user.id, self.id)
        self.assertEqual(False, result, "Should be nothing")

        result = self.model.setPermission(self.user.id, self.id)
        self.assertEqual(None, result['type'], "Should have a type of None. No special permissions")
        self.assertEqual(self.id, result['objectId'], "Should be nothing or empty list")
        self.assertEqual(self.user.id, result['userId'], "Should be nothing or empty list")
        
        result = self.model.getPermission(self.user.id, self.id)
        self.assertEqual(None, result['type'], "Should have a type of None. No special permissions")
        self.assertEqual(self.id, result['objectId'], "Should be nothing or empty list")
        self.assertEqual(self.user.id, result['userId'], "Should be nothing or empty list")


        #Admin User
        data = {}
        data['type'] = "Admin"
        result = self.model.setPermission(self.adminUser.id, self.id, data)
        self.assertEqual(data['type'], result['type'], "Should have a type of None. No special permissions")
        self.assertEqual(self.id, result['objectId'], "Should be nothing or empty list")
        self.assertEqual(self.adminUser.id, result['userId'], "Should be nothing or empty list")
        
        result = self.model.getPermission(self.adminUser.id, self.id)
        self.assertEqual(data['type'], result['type'], "Should have a type of None. No special permissions")
        self.assertEqual(self.id, result['objectId'], "Should be nothing or empty list")
        self.assertEqual(self.adminUser.id, result['userId'], "Should be nothing or empty list")

        #Get user permissions
        result = self.model.getAllUserPermissions(self.user.id)
        self.assertEqual(1, len(result), "Should have only 1 result in the list")
        
        #Get permissions - Should have admin and user permissions
        result = self.model.getAllPermissions(self.id)
        self.assertEqual(2, len(result), "Should have only 2 result in the list")
        
        #Get permissions of something that doesn't exists
        result = self.model.getAllPermissions(self.id+"anything")
        self.assertEqual(0, len(result), "Should have only 2 result in the list")

        #Get permissions by type none
        result = self.model.getPermissionByType(self.id, None)
        self.assertEqual(1, len(result), "Should only by one with no special permissions")

        #Make general user admin
        data = {}
        data['type'] = 'Admin'
        result = self.model.setPermission(self.user.id, self.id, data)
        self.assertEqual(data['type'], result['type'], "Should have a type of Admin")
        self.assertEqual(self.id, result['objectId'], "Should be Object Id")
        self.assertEqual(self.user.id, result['userId'], "Should be User Id")

        #Get permissions by type Admin
        result = self.model.getPermissionByType(self.id, "Admin")
        self.assertEqual(2, len(result), "Should only by one with no special permissions")

        #Delete general user(Admin Type)
        result = self.model.deletePermission(self.user.id, self.id)
        self.assertEqual(data['type'], result['type'], "Should have a type of Admin")
        self.assertEqual(self.id, result['objectId'], "Should be Object Id")
        self.assertEqual(self.user.id, result['userId'], "Should be User Id")
        
        #Delete general user(Admin Type) - should be false
        result = self.model.deletePermission(self.user.id, self.id)
        self.assertEqual(False, result, "Should be False. Nothing deleted")

        #Get permissions by type Admin
        result = self.model.getPermissionByType(self.id, "Admin")
        self.assertEqual(1, len(result), "Should only by one with no special permissions")
         
    def test_update(self):
        pass

    def test_delete(self):
        pass

    def test_retrieval(self):
        pass

    def test_replace(self):
        pass

    def test_errors(self):
        pass
       

    @patch('pcs.util.appFileManager.create_presigned_url')
    def test_with_patch(self, patch_s3_generate_url):
        pass

        # # stubbing s3 mocked service function for testing
        # patch_s3_generate_url.return_value = 'https://s3.amazonaws.com/app-bucket/test/obj.jpg'


