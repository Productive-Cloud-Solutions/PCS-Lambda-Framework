import boto3
import os
import json
import jinja2
from email import encoders
from email.mime.base import MIMEBase
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


client = boto3.client('ses')
HERE = os.path.dirname(os.path.abspath(__file__))
base_template_folder = os.path.join(HERE, "../templates")


#Can load a file or take template String
def sendEmailAttachTemplate(fromAddress, toAddresses:list, subject, filename, bccAddresses:list=[], ccAddresses:list=[], context=None, template=None, template_str=None, returnToSender=None):
    if not template_str and not template:
        return False

    if template_str:
        html_template = jinja2.Template(template_str)
    elif template:
        template_file = os.path.join(base_template_folder, template)
        html_template = jinja2.Template(open(template_file).read())
    rendered = html_template.render()
    if context:
        rendered = html_template.render(context)
    return sendEmailAttach(fromAddress, toAddresses, subject, rendered, filename, bccAddresses, ccAddresses, asHtml=True)


#Send email with attach
def sendEmailAttach(fromAddress, toAddresses, subject, message, filename, bccAddresses:list=[], ccAddresses:list=[], asHtml=False, returnToSender=None):
    if not fromAddress:
        return False

    if not toAddresses:
        return False
        
    if not subject:
        return False
    
    if not message:
        return False
    
    if not filename:
        return False

    if isinstance(toAddresses, list):
        msg = MIMEMultipart()
        msg["subject"] = subject
        msg["from"] = fromAddress
        msg["to"] = ', '.join(toAddresses)
    elif isinstance(toAddresses, str):
        msg = MIMEMultipart()
        msg["subject"] = subject
        msg["from"] = fromAddress
        msg["to"] = toAddresses

    # Set message body
    body = MIMEText(message, 'plain')

    #If message body is html
    if asHtml:  
        body = MIMEText(message, 'html')
    
    msg.attach(body)

    if filename:
        file = os.path.join(base_template_folder, filename)
        with open(file, "rb") as attachment:
            part = MIMEApplication(attachment.read())
            part.add_header("Content-Disposition",
                            "attachment",
                            filename=filename)
        msg.attach(part)

    if isinstance(toAddresses, str):
        destinations = [toAddresses]
    elif isinstance(toAddresses, list):
        destinations = toAddresses
    
    response = client.send_raw_email(
        Source=fromAddress,
        Destinations=destinations,
        RawMessage={"Data": msg.as_string()}
    )
    return response


#Can load a file or take template String
def sendEmailTemplate(fromAddress, toAddresses:list, subject, bccAddresses:list=[], ccAddresses:list=[], context=None, template=None, template_str=None, returnToSender=None):
    if not template_str and not template:
        return False

    if template_str:
        html_template = jinja2.Template(template_str)
    elif template:
        template_file = os.path.join(base_template_folder, template)
        html_template = jinja2.Template(open(template_file).read())
    rendered = html_template.render()
    if context:
        rendered = html_template.render(context)
    return sendEmail(fromAddress, toAddresses, subject, rendered, bccAddresses, ccAddresses, asHtml=True)


#   Since this is not a controller, don't raise exceptions,
#   just return False if one of the parameters is missing
def sendEmail(fromAddress, toAddresses:list, subject, message, bccAddresses:list=[], ccAddresses:list=[], asHtml=False, returnToSender=None):
    if not toAddresses:
        return False
    elif isinstance(toAddresses, str): #If toAddresses is not missing check if it is a string
        toAddresses = [toAddresses] #Convert string value of toAddresses to a list and overwrite it.

    if not subject:
        return False
    
    if not message:
        return False
    
    if not fromAddress:
        return False
    
    destination = {
        'ToAddresses': toAddresses, #To Address list
    }
    
    if ccAddresses:
        destination['CcAddresses']=ccAddresses
    
    if bccAddresses:
        destination['BccAddresses']=bccAddresses

    body = {
        "Text": {
            'Charset': 'UTF-8',
            "Data": message
        }
    }

    if asHtml:  
        body = {
            'Html': {
                    'Charset': 'UTF-8',
                    'Data': message
                }
        }

    #Call SES send_email API
    response = client.send_email(
        Source = fromAddress, #Sent from email
        Destination=destination,
        Message={
            'Subject': {
                'Charset': 'UTF-8',
                'Data': subject
            },
            'Body': body
        },

        # If theses 4 are empty, don't declare these. This causes the function to fail
        # ReplyToAddresses=[], #Can be empty
        # ReturnPath='', #Can be empty
        # ReturnPathArn='', #Can be empty
        # SourceArn='', #Can be empty


        # Tags=[
        #     {
        #         'Name': 'string',
        #         'Value': 'string'
        #     },
        # ],
        # ConfigurationSetName='string'
    )

    # print(response)
    return response