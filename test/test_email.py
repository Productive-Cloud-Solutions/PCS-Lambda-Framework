# test for notes API
import os
import app
import uuid
import boto3
import unittest
import time
import random
from Python_Requirements_Layer.python import jinja2
import tempfile
from email import encoders
from email.mime.base import MIMEBase
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from Python_Requirements_Layer.python.fpdf import FPDF
from datetime import datetime
from unittest.mock import patch, MagicMock, Mock
from pcs.util.mailer import sendEmail, sendEmailTemplate, sendEmailAttach, sendEmailAttachTemplate
from pcs.testing.test_creator import TestUser, createEvent, createUser, LambdaTester


tester = LambdaTester(app.lambda_handler)
# user_model = User()


class GeneralTest(unittest.TestCase):

    def setUp(self):
        self.user = TestUser().createUser()

        self.user2 = TestUser().createUser()
        self.fromEmail = "server@productivecloudsolutions.com"
        self.toEmail = "pcstestemailuser@productiveclouds.com"
        self.pdf = FPDF()
        # self.renderHtml = open("./templates/test_only.html").read()

    def test_send_email(self):
        # ccEmails = []
        message = "This is a test email from PCS Backend Workspace"
        subject = "Testing boto Email"
        result = sendEmail(toAddresses=self.toEmail,
                           fromAddress=self.fromEmail, message=message, subject=subject)

        self.assertIn("MessageId", result, "Email was not sent")

    def test_send_email_as_html(self):
        # Render template w/out context
        template_str = "<h1>Test</h1><p>This is a test email from PCS Backend Workspace</p>"
        subject = "Testing Boto Html Email"
        result = sendEmailTemplate(
            toAddresses=self.toEmail, fromAddress=self.fromEmail, template_str=template_str, subject=subject)

        self.assertIn("MessageId", result, "Email was not sent")

        # Render template w/ context
        template_str = "<h1>{{context_header}}</h1><p>This is a test email {{made_by}} from PCS Backend Workspace w/ Context</p>"
        context = {
            "context_header": "My Header from Context",
            "made_by": "Made by DeJurnett"
        }
        subject = "Testing Boto Html Email w/ Context"
        result = sendEmailTemplate(toAddresses=self.toEmail, fromAddress=self.fromEmail,
                                   context=context, template_str=template_str, subject=subject)

        self.assertIn("MessageId", result, "Email was not sent")

        # Render template w/ context but don't pass context
        template_str = "<h1>{{context_header}}</h1><p>This is a test email {{made_by}} from PCS Backend Workspace w/ Context</p>"
        # context = {
        #     "context_header": "My Header from Context",
        #     "made_by": "Made by DeJurnett"
        # }
        subject = "Testing Boto Html Email w/ Context but Context was not Passed"
        result = sendEmailTemplate(
            toAddresses=self.toEmail, fromAddress=self.fromEmail, template_str=template_str, subject=subject)

        self.assertIn("MessageId", result, "Email was not sent")
    
    def test_send_email_as_html_file(self):
        # Render template as file w/out context
        subject = "Testing Boto Html File Email"
        result = sendEmailTemplate(
            toAddresses=self.toEmail, fromAddress=self.fromEmail, template="test_only.html", subject=subject)

        self.assertIn("MessageId", result, "Email was not sent")
        
        # Render template as file w/ context
        subject = "Testing Boto Html File Email w/ Context"
        context = {
            "context_header": "My Context in Latin : "
        }
        result = sendEmailTemplate(
            toAddresses=self.toEmail, fromAddress=self.fromEmail, context=context, template="test_only.html", subject=subject)

        self.assertIn("MessageId", result, "Email was not sent")

    def test_send_email_w_attach(self):
        f = tempfile.NamedTemporaryFile(mode='w', delete=False)
        self.pdf.output(f.name, 'F')

        message = "This is a test email from PCS Backend Workspace"
        subject = "Testing boto Email w/ Attachment"
        result = sendEmailAttach(toAddresses=self.toEmail,
                           fromAddress=self.fromEmail, message=message, subject=subject, filename=f.name)

        self.assertIn("MessageId", result, "Email was not sent")
        
        #Multiple to Addresses
        self.toEmail = [self.toEmail]
        self.toEmail.append("pcstestemailuser@productiveclouds.com")

        f = tempfile.NamedTemporaryFile(mode='w', delete=False)
        self.pdf.output(f.name, 'F')

        message = "This is a test email from PCS Backend Workspace"
        subject = "Testing boto Email w/ Attachment"
        result = sendEmailAttach(toAddresses=self.toEmail,
                           fromAddress=self.fromEmail, message=message, subject=subject, filename=f.name)

        self.assertIn("MessageId", result, "Email was not sent")
    
    def test_send_email_w_attach_html(self):
        f = tempfile.NamedTemporaryFile(mode='w', delete=False)
        self.pdf.output(f.name, 'F')

        # Render template_str w/out context
        template_str = "<h1>Test</h1><p>This is a test email from PCS Backend Workspace</p>"
        subject = "Testing boto Email w/ Attachment and HTML template_str"
        result = sendEmailAttachTemplate(
            toAddresses=self.toEmail, fromAddress=self.fromEmail, filename=f.name, template_str=template_str, subject=subject)

        self.assertIn("MessageId", result, "Email was not sent")

        # Render template file w/out context
        subject = "Testing boto Email w/ Attachment and HTML template file"
        result = sendEmailAttachTemplate(
            toAddresses=self.toEmail, fromAddress=self.fromEmail, filename=f.name, template="test_only.html", subject=subject)

        self.assertIn("MessageId", result, "Email was not sent")
        
  
        # Render template_str w/ context
        template_str = "<h1>{{context_header}}</h1><p>This is a test email from PCS Backend Workspace</p>"
        context = {
            "context_header": "My Context: "
        }
        subject = "Testing boto Email w/ Attachment and HTML template_str"
        result = sendEmailAttachTemplate(
            toAddresses=self.toEmail, fromAddress=self.fromEmail, filename=f.name, template_str=template_str, subject=subject, context=context)

        self.assertIn("MessageId", result, "Email was not sent")

        #Render template file w/ context
        context = {
            "context_header": "My Context in Latin : "
        }
        # Render template w/out context
        subject = "Testing boto Email w/ Attachment and HTML template file"
        result = sendEmailAttachTemplate(
            toAddresses=self.toEmail, fromAddress=self.fromEmail, filename=f.name, template="test_only.html", subject=subject, context=context)

        self.assertIn("MessageId", result, "Email was not sent")
    
    @patch("pcs.util.mailer.sendEmailAttach")
    def test_send_email_w_attach_html(self, mailer_mock:MagicMock):
        mailer_mock.return_value = True
        
        f = tempfile.NamedTemporaryFile(mode='w', delete=False)
        self.pdf.output(f.name, 'F')

        # Render template_str w/out context
        template_str = "<h1>Test</h1><p>This is a test email from PCS Backend Workspace</p>"
        subject = "Testing boto Email w/ Attachment and HTML template_str"
        result = sendEmailAttachTemplate(
            toAddresses=self.toEmail, fromAddress=self.fromEmail, filename=f.name, template_str=template_str, subject=subject)

        self.assertIn(f.name, mailer_mock.call_args.args, "Temp File name is not present")
        self.assertIn(template_str, mailer_mock.call_args.args, "Template string was not passed")
        self.assertEqual(True, result, "Mock return value was not set")
        
        #Test with html file and attachment
        f = tempfile.NamedTemporaryFile(mode='w', delete=False)
        self.pdf.output(f.name, 'F')

        # Render template_str w/out context
        subject = "Testing boto Email w/ Attachment and HTML template"
        context = {
            "context_header": "My Context in Latin : "
        }
        result = sendEmailAttachTemplate(
            toAddresses=self.toEmail, fromAddress=self.fromEmail, filename=f.name, template="test_only.html", subject=subject, context=context)

        self.assertIn(f.name, mailer_mock.call_args.args, "Temp File name is not present")
        self.assertIn(context['context_header'], mailer_mock.call_args.args[3], "Template string was not passed")
        self.assertEqual(True, result, "Mock return value was not set")

    @patch("pcs.util.mailer.client.send_email")
    def test_send_email_mock(self, mailer_mock: MagicMock):
        mailer_mock.return_value = True
        # ccEmails = []
        message = "This is a test email from PCS Backend Workspace"
        subject = "Testing boto Email"
        body = {
            "Text": {
                'Charset': 'UTF-8',
                "Data": message
            }
        }
        destination = {
            'ToAddresses': [self.toEmail],  # To Address list"
        }
        msg = {
            'Subject': {
                'Charset': 'UTF-8',
                'Data': subject
            },
            'Body': body
        }
        result = sendEmail(toAddresses=self.toEmail,
                           fromAddress=self.fromEmail, message=message, subject=subject)
        mailer_mock.assert_called_once_with(Source=self.fromEmail, Destination=destination, Message=msg)

        self.assertEqual(True, result, "Email was not sent")

    @patch("pcs.util.mailer.sendEmail")
    def test_send_email_as_html_mock(self, mailer_mock:MagicMock):
        mailer_mock.return_value = True
        # Render template w/out context
        template_str = "<h1>Test</h1><p>This is a test email from PCS Backend Workspace</p>"
        subject = "Testing Boto Html Email"
        result = sendEmailTemplate(
            toAddresses=self.toEmail, fromAddress=self.fromEmail, template_str=template_str, subject=subject)
        # print(mailer_mock.call_args_list)
        self.assertIn(template_str, mailer_mock.call_args.args)

        self.assertEqual(True, result, "Email was not sent")

        # Render template w/ context
        template_str = "<h1>{{context_header}}</h1><p>This is a test email {{made_by}} from PCS Backend Workspace w/ Context</p>"
        context = {
            "context_header": "My Header from Context",
            "made_by": "Made by DeJurnett"
        }
        subject = "Testing Boto Html Email w/ Context"
        result = sendEmailTemplate(toAddresses=self.toEmail, fromAddress=self.fromEmail,
                                   context=context, template_str=template_str, subject=subject)

        self.assertIn(context['context_header'], mailer_mock.call_args.args[3])
        self.assertIn(context['made_by'], mailer_mock.call_args.args[3])
        self.assertEqual(True, result, "Email was not sent")

        # Render template w/ context but don't pass context
        template_str = "<h1>{{context_header}}</h1><p>This is a test email {{made_by}} from PCS Backend Workspace w/ Context</p>"
        subject = "Testing Boto Html Email w/ Context but Context was not Passed"
        result = sendEmailTemplate(
            toAddresses=self.toEmail, fromAddress=self.fromEmail, template_str=template_str, subject=subject)
        
        self.assertNotIn(context['context_header'], mailer_mock.call_args.args[3])
        self.assertNotIn(context['made_by'], mailer_mock.call_args.args[3])
        self.assertEqual(True, result, "Email was not sent")
    
    @patch("pcs.util.mailer.sendEmail")
    def test_send_email_as_html_file_mock(self, mailer_mock:MagicMock):
        mailer_mock.return_value = True
        # Render template as file w/out context
        subject = "Testing Boto Html File Email"
        result = sendEmailTemplate(
            toAddresses=self.toEmail, fromAddress=self.fromEmail, template="test_only.html", subject=subject)
        context = {
            "context_header": "My Context in Latin : "
        }
        self.assertNotIn(context["context_header"], mailer_mock.call_args.args[3])
        self.assertEqual(True, result, "Email was not sent")
        
        # Render template as file w/ context
        subject = "Testing Boto Html File Email w/ Context"

        result = sendEmailTemplate(
            toAddresses=self.toEmail, fromAddress=self.fromEmail, context=context, template="test_only.html", subject=subject)
        
        self.assertIn(context["context_header"], mailer_mock.call_args.args[3])
        self.assertEqual(True, result, "Email was not sent")

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
