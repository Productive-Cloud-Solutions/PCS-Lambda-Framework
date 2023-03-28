import uuid
import json
import boto3
import os
import logging
from botocore.exceptions import ClientError

# s3 = boto3.client('s3')
s3 = boto3.client('s3')
BUCKET = "drop-code.cli.conditionedminds"

if not os.environ.get('AWS_SAM_LOCAL'):
    BUCKET = os.environ.get('APP_BUCKET')

def create_presigned_url( object_name, bucket_name=BUCKET, expiration=3600):
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    # Generate a presigned URL for the S3 object
    s3_client = boto3.client('s3')
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response

def getAppUploadURL(basePath, fileName, owner='default', expiration=3600, override=True):
    
    uploadURI = os.path.join(basePath,owner,fileName)
    if not override:
        uploadURI = os.path.join(basePath,owner,str(uuid.uuid4()),fileName)

    s3_client = boto3.client('s3')
    try:
        response = s3_client.generate_presigned_post(BUCKET,uploadURI,ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL

    return {
        'objectURL':create_presigned_url(uploadURI),
        'uploadURL':response['url'],
        'objectURI':uploadURI,
        'fields':  json.dumps(response['fields'])
    }

def delete_file(key,bucket_name=BUCKET):
    return s3.delete_object(Bucket=bucket, Key=key)

def move(source_key, dest_key, bucket_name=BUCKET):
    # copy to new name 
    copy(source_key,dest_key,bucket_name,bucket_name)

    # Delete the former object A
    s3_resource.Object(bucket_name, source_key).delete()

def copy(source_key, dest_key, source_bucket=BUCKET, dest_bucket=BUCKET)-> object:
    s3_resource = boto3.resource('s3')
    copy_source = {
        'Bucket': source_bucket,
        'Key': source_key
    }
    bucket = s3_resource.Bucket(dest_bucket)
    bucket.copy(copy_source, dest_key)


    return {
        'url': create_presigned_url(dest_key),
        'uri': dest_key
    }