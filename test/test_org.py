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

from pcs.models.org import Organization, OrgFile

class GeneralTest(unittest.TestCase):

    def setUp(self):
        self.user = TestUser().createUser()
        self.org = Organization()
        self.id = str(uuid.uuid4())
        # self.user2 = TestUser().createUser()

    def tearDown(self) -> None:
        self.org.db.drop_collection(self.org.files.table)
        self.org.db.drop_collection(self.org.files.permissions.table)
        return super().tearDown()


    def test_add_image(self):
        result = self.org.addImage(self.id)
        self.assertIn("id", result, "_id was not in result")
        self.assertIn("org", result, "org was not in result")
        self.assertEqual(self.id, result['org'], "Org was not passed or set")

        
    def test_get_images(self):
        result = self.org.addImage(self.id)
        self.assertIn("id", result, "id was not in result")
        self.assertIn("org", result, "org was not in result")
        self.assertEqual(self.id, result['org'], "Org was not passed or set")
        
        result = self.org.getImages(self.id)
        for r in result:
            self.assertEqual(self.id, r['org'], "Org was not passed or set")
            for o in r[self.org.files.permissions.table]:
                self.assertEqual(self.id, o['userId'])
        
    def test_delete(self):
        pass
        
    def test_retrieval(self):
        pass
        
    """
    Ignore this for now.
    """
    @patch('pcs.util.appFileManager.create_presigned_url')
    def test_with_patch(self, patch_s3_generate_url):
        pass

        # stubbing s3 mocked service function for testing
        # patch_s3_generate_url.return_value = 'https://s3.amazonaws.com/app-bucket/test/obj.jpg'


