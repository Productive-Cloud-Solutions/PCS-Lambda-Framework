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

tester = LambdaTester(app.lambda_handler)

class GeneralTest(unittest.TestCase):

    """
    This is where you set up things you will use across all test
    """
    def setUp(self):
        pass
        """
        Create a couple default users
        """
        # self.user = TestUser().createUser()
        # self.user2 = TestUser().createUser()
        # self.doctor = TestUser().createUser()
        # self.doctor2 = TestUser().createUser()

    """
    CRUD: C - Create
    This is specifically testing the creation of an item in
    the Mongo Database.
    """
    def test_create(self):
        pass
        """
        Create the payload and assign appropriate values to the item you are trying to create
        You don't need to assign an ID or else we will get an error
        """
        #Create appointment
        # payload = {}
        # payload['doctor_id'] = self.doctor.id
        # payload['appointment'] = {}
        # payload['appointment']['from'] = "2022-10-01T18:00:00"
        # payload['appointment']['to'] = "2022-10-01T19:00:00"
        # payload['appointment']['reason'] = "Physical Exam"
        # payload['appointment']['type'] = "in_person"

        """
        This is sent to the app. "bookAppointment" would refer to the action the event must take.
        In this case we want to create an appointment, and the user is the person that is requesting the action
        Payload is the data that is being passed to the controller and thus sent to the model.
        Result is then sent back by the method and the app
        """
        # result = tester.createEvent("bookAppointment", user=self.user, payload=payload)


        """
        We use the result to check against the data we sent in from the payload
        If it returns something different then we made a mistake in the controller or model we are testing
        """
        # self.assertEqual(result['doctor'], self.doctor.id, "Wrong user Id passed")
        # self.assertEqual(result['patient'], self.user.id, "Wrong user Id passed")
        # self.assertEqual(result['from'], payload['appointment']['from'], "Wrong Interval Passed")
        # self.assertEqual(result['to'], payload['appointment']['to'], "Wrong Interval Passed")
        # self.assertEqual(result['reason'], payload['appointment']['reason'], "Wrong Reason passed")
        # self.assertEqual(result['type'], payload['appointment']['type'], "Wrong Type passed")


        """
        Testing an error that comes from the creation of the item in the model
        """
        #No Reason
        # payload = {}
        # payload['doctor_id'] = self.doctor.id
        # payload['appointment'] = {}
        # payload['appointment']['from'] = "2022-07-01T18:00:00" 
        # payload['appointment']['to'] = "2022-07-01T19:00:00"
        # payload['appointment']['reason'] = None
        # payload['appointment']['type'] = "in_person"

        """
        We use self.assertRaises(Exception) to catch all exceptions the method we are testing
        """
        # with self.assertRaises(Exception) as error:
        #     result = tester.createEvent("bookAppointment", user=self.user, payload=payload)
        """
        This is how we check for the specific error(Exception) we wanted to have returned to the user
        """
        # self.assertEqual("Reason cannot be missing or empty", error.exception.args[0], "Wrong id passed")
        

    """
    CRUD: U - Update
    This is for testing the update of a record from the
    Mongo Database. The record must be created first, then
    you can update that record that was created
    """
    def test_update(self):
        pass
        """
        Create the item first
        """
        #Create appointment
        # payload = {}
        # payload['doctor_id'] = self.doctor.id
        # payload['appointment'] = {}
        # payload['appointment']['from'] = "2022-10-01T18:00:00" 
        # payload['appointment']['to'] = "2022-10-01T19:00:00"
        # payload['appointment']['reason'] = "Physical Exam"
        # payload['appointment']['type'] = "in_person"

        # result = tester.createEvent("bookAppointment", user=self.user, payload=payload)

        # self.assertEqual(result['doctor'], self.doctor.id, "Wrong user Id passed")
        # self.assertEqual(result['patient'], self.user.id, "Wrong user Id passed")
        # self.assertEqual(result['from'], payload['appointment']['from'], "Wrong Interval Passed")
        # self.assertEqual(result['to'], payload['appointment']['to'], "Wrong Interval Passed")
        # self.assertEqual(result['reason'], payload['appointment']['reason'], "Wrong Reason passed")
        # self.assertEqual(result['type'], payload['appointment']['type'], "Wrong Type passed")
        
        """
        Now we try to update the item we created
        """
        # payload = {}
        # payload['id'] = result['id'] #Appointment Id
        # payload['appointment'] = {}
        # payload['appointment']['from'] = "2022-10-30T18:00:00" 
        # payload['appointment']['to'] = "2022-10-30T19:00:00"
        # payload['appointment']['reason'] = "COVID TEST"
        # payload['appointment']['type'] = "video"
        
        # result = tester.createEvent("updateAppointment", user=self.user, payload=payload)

        # self.assertEqual(result['doctor'], self.doctor.id, "Wrong user Id passed")
        # self.assertEqual(result['patient'], self.user.id, "Wrong user Id passed")
        # self.assertEqual(result['from'], payload['appointment']['from'], "Wrong Interval Passed")
        # self.assertEqual(result['to'], payload['appointment']['to'], "Wrong Interval Passed")
        # self.assertEqual(result['reason'], payload['appointment']['reason'], "Wrong Reason passed")
        

    """
    CRUD: D - Delete
    This is for testing the deletion of a record from the
    Mongo Database. The record must be created first, then
    you can delete that record that was created
    """
    def test_delete(self):
        pass
        """
        Create the item first. This is going to occur throughout testing
        """
        #Create appointment
        # payload = {}
        # payload['doctor_id'] = self.doctor.id
        # payload['appointment'] = {}
        # payload['appointment']['from'] = "2022-10-01T18:00:00" 
        # payload['appointment']['to'] = "2022-10-01T19:00:00"
        # payload['appointment']['reason'] = "Physical Exam"
        # payload['appointment']['type'] = "in_person"

        # result = tester.createEvent("bookAppointment", user=self.user, payload=payload)

        # self.assertEqual(result['doctor'], self.doctor.id, "Wrong user Id passed")
        # self.assertEqual(result['patient'], self.user.id, "Wrong user Id passed")
        # self.assertEqual(result['from'], payload['appointment']['from'], "Wrong Interval Passed")
        # self.assertEqual(result['to'], payload['appointment']['to'], "Wrong Interval Passed")
        # self.assertEqual(result['reason'], payload['appointment']['reason'], "Wrong Reason passed") 
        # self.assertEqual(result['type'], payload['appointment']['type'], "Wrong Type passed")

        """
        Once we create the item, then we can attempt to delete it by using the result's id
        You can only do this if the creation happened just before the delete.
        """
        #Delete Appointment
        # payload = {}
        # payload['id'] = result['id']
        
        # result = tester.createEvent("deleteAppointment", user=self.user, payload=payload)

        # self.assertEqual(result['id'], payload['id'], "Wrong Appointment deleted")
        # self.assertEqual(result['doctor'], self.doctor.id, "Wrong user Id passed")
        # self.assertEqual(result['patient'], self.user.id, "Wrong user Id passed")
        
        """
        Create an appointment for error testing of delete
        """
        #Create appointment
        # payload = {}
        # payload['doctor_id'] = self.doctor.id
        # payload['appointment'] = {}
        # payload['appointment']['from'] = "2022-10-01T18:00:00" 
        # payload['appointment']['to'] = "2022-10-01T19:00:00"
        # payload['appointment']['reason'] = "Physical Exam"
        # payload['appointment']['type'] = "in_person"


        # result = tester.createEvent("bookAppointment", user=self.user, payload=payload)

        # self.assertEqual(result['doctor'], self.doctor.id, "Wrong user Id passed")
        # self.assertEqual(result['patient'], self.user.id, "Wrong user Id passed")
        # self.assertEqual(result['from'], payload['appointment']['from'], "Wrong Interval Passed")
        # self.assertEqual(result['to'], payload['appointment']['to'], "Wrong Interval Passed")
        # self.assertEqual(result['reason'], payload['appointment']['reason'], "Wrong Reason passed") 
        # self.assertEqual(result['type'], payload['appointment']['type'], "Wrong Type passed")

        """
        User does not own the item they are deleteing, so they should not be able to do so.
        """
        #Errors
        #Another User trying to delete some else's appointment
        # payload = {}
        # payload['id'] = result['id']
        
        # with self.assertRaises(Exception) as error:
        #     result = tester.createEvent("deleteAppointment", user=self.doctor2, payload=payload)
        # self.assertEqual("Cannot delete another's appointment!!!", error.exception.args[0], "Wrong id passed")
        
        """
        The user does not exist, so they should not be able to delete
        """
        #User not found or Doesn't Exist
        # payload = {}
        # payload['id'] = result['id']
        
        # with self.assertRaises(Exception) as error:
        #     result = tester.createEvent("deleteAppointment", user=None, payload=payload)
        # self.assertEqual("User was not found or does not exist", error.exception.args[0], "Wrong id passed")

    """
    CRUD: R - Read (Single)
    This is for testing the retrival (read/get) of a single record from the
    Mongo Database. The record must be created first, then
    you can get that record that was created

    You can test your retrival errors here.
    """
    def test_retrieval(self):
        pass
        """
        Similar to update and delete, in order to test retrieval(get), you need to create
        the object first.
        """
        #Create appointment
        # payload = {}
        # payload['doctor_id'] = self.doctor.id
        # payload['appointment'] = {}
        # payload['appointment']['from'] = "2022-10-01T18:00:00" 
        # payload['appointment']['to'] = "2022-10-01T19:00:00"
        # payload['appointment']['reason'] = "Physical Exam"
        # payload['appointment']['type'] = "in_person"

        # result = tester.createEvent("bookAppointment", user=self.user, payload=payload)

        # self.assertEqual(result['doctor'], self.doctor.id, "Wrong user Id passed")
        # self.assertEqual(result['patient'], self.user.id, "Wrong user Id passed")
        # self.assertEqual(result['from'], payload['appointment']['from'], "Wrong Interval Passed")
        # self.assertEqual(result['to'], payload['appointment']['to'], "Wrong Interval Passed")
        # self.assertEqual(result['reason'], payload['appointment']['reason'], "Wrong Reason passed")
        # self.assertEqual(result['type'], payload['appointment']['type'], "Wrong Type passed")
        
        """
        Using the result id from the creation step (or you can save the result id to a variable
        to user over and over again) and you can use that to pass
        to the retrieval.
        """
        # appointmentId = result['id']
        # payload = {}
        # payload['id'] = appointmentId

        # result = tester.createEvent("getAppointment", user=self.user, payload=payload)

        # self.assertEqual(result['id'], appointmentId, "Wrong Id Passed")
        # self.assertEqual(result['doctor'], self.doctor.id, "Wrong user Id passed")
        # self.assertEqual(result['patient'], self.user.id, "Wrong user Id passed")
        
        """
        Error testing takes place, and as mentioned before, you can test the errors for each function
        in their respective methods, or you can test them all in the errors function (Choice is yours).
        """
        #Errors
        #User not found or Doesn't Exist
        # appointmentId = result['id']
        # payload = {}
        # payload['id'] = appointmentId

        # with self.assertRaises(Exception) as error:
        #     result = tester.createEvent("getAppointment", user=None, payload=payload)
        # self.assertEqual("User was not found or does not exist", error.exception.args[0], "Wrong id passed")
    

        #Another User trying to delete some else's appointment
        # appointmentId = result['id']
        # payload = {}
        # payload['id'] = appointmentId

        # with self.assertRaises(Exception) as error:
        #     result = tester.createEvent("getAppointment", user=self.doctor2, payload=payload)
        # self.assertEqual("Cannot get another's appointment!!!", error.exception.args[0], "Wrong id passed")

    """
    CRUD: R - Read (Multiple)
    This is for testing the retrival (read/get) of multiple records from the
    Mongo Database. The record must be created first, then
    you can get that record that was created
    """
    def test_retrievals(self):
        pass
        """
        Create the 1st item belonging to the user
        """
        #Create appointment 1 with doctor
        # payload = {}
        # payload['doctor_id'] = self.doctor.id
        # payload['appointment'] = {}
        # payload['appointment']['from'] = "2022-10-01T18:00:00" 
        # payload['appointment']['to'] = "2022-10-01T19:00:00"
        # payload['appointment']['reason'] = "Physical Exam"
        # payload['appointment']['type'] = "in_person"

        # result = tester.createEvent("bookAppointment", user=self.user, payload=payload)

        # self.assertEqual(result['doctor'], self.doctor.id, "Wrong user Id passed")
        # self.assertEqual(result['patient'], self.user.id, "Wrong user Id passed")
        # self.assertEqual(result['from'], payload['appointment']['from'], "Wrong Interval Passed")
        # self.assertEqual(result['to'], payload['appointment']['to'], "Wrong Interval Passed")
        # self.assertEqual(result['reason'], payload['appointment']['reason'], "Wrong Reason passed")
        # self.assertEqual(result['type'], payload['appointment']['type'], "Wrong Type passed")

        """
        Create the second item belonging to the user
        """
        #Create appointment 2 with doctor2
        # payload = {}
        # payload['doctor_id'] = self.doctor2.id
        # payload['appointment'] = {}
        # payload['appointment']['from'] = "2022-10-30T18:00:00" 
        # payload['appointment']['to'] = "2022-10-30T19:00:00"
        # payload['appointment']['reason'] = "Physical Exam"
        # payload['appointment']['type'] = "in_person"

        # result = tester.createEvent("bookAppointment", user=self.user, payload=payload)

        # self.assertEqual(result['doctor'], self.doctor2.id, "Wrong user Id passed")
        # self.assertEqual(result['patient'], self.user.id, "Wrong user Id passed")
        # self.assertEqual(result['from'], payload['appointment']['from'], "Wrong Interval Passed")
        # self.assertEqual(result['to'], payload['appointment']['to'], "Wrong Interval Passed")
        # self.assertEqual(result['reason'], payload['appointment']['reason'], "Wrong Reason passed")
        # self.assertEqual(result['type'], payload['appointment']['type'], "Wrong Type passed")
        
        """
        Get the items based on the user. Id is usually not passed to this method, but
        it depends on the app we are designing. Instead of checking the contents of the
        retrievals method, we are checking the number of items received, since it 
        returns a list.
        """
        #Get User's Appointments
        # result = tester.createEvent("getAppointments", user=self.user)
        # self.assertEqual(len(result), 2, "Wrong number of appointments passed")

        """
        Error testing takes place, and as mentioned before, you can test the errors for each function
        in their respective methods, or you can test them all in the errors function (Choice is yours).
        """
        #Errors
        # with self.assertRaises(Exception) as error:
        #     result = tester.createEvent("getAppointments", user=None, payload=payload)
        # self.assertEqual("User was not found or does not exist", error.exception.args[0], "Wrong id passed")
    

    """
    You don't have to specifically test the errors here, but
    it is up to you. I would test them in the specific test I am working with.
    """
    def test_errors(self):
        pass
        # payload = {}
        # payload['categories'] = ['Wrong Code']
        # with self.assertRaises(Exception) as error:
        #     result = tester.createEvent("getTranscript", user=self.user,
        #                             _id=False, modifiedTimeStamp=False, payload= payload)
        # self.assertIn('The code is not valid',
        #               error.exception.args[0], 'Wrong Error received')
