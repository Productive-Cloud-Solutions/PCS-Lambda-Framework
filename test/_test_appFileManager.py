import app
import uuid
import json
import unittest #TODO look up this!
import requests

from pcs.util import appFileManager

create_event = {
    "identity":{"claims": {"sub": "test-8004-443f-9c1b-66490ec68841"}, "sub": "test-8004-443f-9c1b-66490ec68841", "username": "emanuelp7"},
    "action":"createMessage",
    "payload":{
        "conversationID":"test2-8004-443f-9c1b-66490ec68841",
        "message": "Hello from the test script function",
        "id":"xccxwqewresd-23uyu327uy-287uy32378-2ew323",
        "from":"test-8004-443f-9c1b-66490ec68841",
        "created": "2020-11-06T07:15:41.111Z",
        "modified": "2020-11-06T07:15:41.111Z"
    }
}

delete_event = {
    "identity":{"claims": {"sub": "test-8004-443f-9c1b-66490ec68841"}, "sub": "test-8004-443f-9c1b-66490ec68841", "username": "emanuelp7"},
    "action":"deleteMessage",
    "payload":{
        "conversationID":"test2-8004-443f-9c1b-66490ec68841",
        "messageID":"test2-8004-443f-9c1b-66490ec68841",
    }
}

get_event = {
    "identity":{"claims": {"sub": "test-8004-443f-9c1b-66490ec68841"}, "sub": "test-8004-443f-9c1b-66490ec68841", "username": "emanuelp7"},
    "action":"getMessages",
    "payload":{
        "conversationID":"test2-8004-443f-9c1b-66490ec68841",
    }
}

#TODO pick a file to clone a write a test case Check i s the function returned the correct data


class Test(unittest.TestCase):

    def setUp(self):
        self.userID = str(uuid.uuid4())
        self.id = str(uuid.uuid4())

    # def test_create(self):
    #     details = appFileManager.getAppUploadURL('some/path/','myfile.txt','system-test-user')
    #     self.assertIn('some/path/', details['fields'], 'Wrong Upload URL')
    #     self.assertIn('myfile.txt', details['fields'], 'Wrong Upload URL')
    #     self.assertIn('system-test-user', details['fields'], 'Wrong Upload URL')
    #     self.assertIn('some/path/', details['objectURI'], 'Wrong URI URL')
    #     self.assertIn('myfile.txt', details['objectURI'], 'Wrong URI URL')
    #     self.assertIn('system-test-user', details['objectURI'], 'Wrong URI URL')
    #     self.assertIn('some/path/', details['objectURL'], 'Wrong URI URL')
    #     self.assertIn('myfile.txt', details['objectURL'], 'Wrong URI URL')
    #     self.assertIn('system-test-user', details['objectURL'], 'Wrong URI URL')
    #     self.assertIn('https://', details['objectURL'], 'Wrong URI URL')

    #     # make file 
    #     f = open('/tmp/good.txt','w')
    #     f.write(self.id)
    #     f.close()
    #     # open file
    #     f = open('/tmp/good.txt','rb')
    #     files = {'file': (details['objectURI'], f)}
    #     # upload file 
    #     response = requests.post(details['uploadURL'], data=json.loads(details['fields']), files=files)
    #     self.assertEqual(response.ok, True, "Upload Failed!")

    #     # Get File Using provided url
    #     uploadedFile = requests.get(details['objectURL'])
    #     self.assertEqual(uploadedFile.text, self.id, 'Failed to download correct file')
        
    #     # Get File Using New Presigned Url
    #     url = appFileManager.create_presigned_url(details['objectURI'])
    #     uploadedFile = requests.get(url)
    #     self.assertEqual(uploadedFile.text, self.id, 'Failed to download correct file')


        

    def test_get(self):
        pass
    
    def test_delete(self):
        pass

    def test_update(self):
        pass


    def tearDown(self):
        pass