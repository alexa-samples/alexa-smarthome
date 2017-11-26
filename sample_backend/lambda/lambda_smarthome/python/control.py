import boto3
import json
import os
import urllib.request

from datetime import datetime, timedelta, timezone
from zipfile import ZipFile


api_aws = boto3.client('apigateway')
cf_aws = boto3.client('cloudformation')
iot_aws = boto3.client('iot')
lambda_aws = boto3.client('lambda')
s3_aws = boto3.client('s3')

package_filename = 'skill-package.zip'
sample_uri = 'https://raw.githubusercontent.com/alexa/alexa-smarthome/master/sample_messages/'

def json_output(dict):
    return print(json.dumps(dict, indent=2))


def deploy():
    if not os.path.isfile(package_filename):
        print('ERR', package_filename, 'file not found')
        return

    with open(package_filename, 'rb') as file_data:
        s3_aws.upload_fileobj(file_data, 'endpoint-code-us', package_filename)
        print('Deployed: S3')

    zip_package = open(package_filename, "rb")
    response = lambda_aws.update_function_code(
        FunctionName='SampleSkillAdapter',
        ZipFile=zip_package.read()
    )

    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        print('Deployed: Lambda')
    else:
        print(response)


def pack_folder(zip, folder):
    for root, dirs, files in os.walk(folder):
        for file in files:
            # Strip out compiled Python
            filename, file_extension = os.path.splitext(file)
            if file_extension == '.pyc':
                continue
            zip.write(os.path.join(root, file))


def pack():
    print('Starting packaging')
    if os.path.isfile(package_filename):
        os.remove(package_filename)
        print('Removed', package_filename)

    print('Zipping package contents')
    with ZipFile(package_filename, 'w') as zip_package:
        zip_package.write('index.py')

    print('Ending packaging')
    return


def push():
    pack()
    deploy()


def status():
    # Get the modification times of the Stack, Lambda, and S3 Bucket

    # Stack
    cf_stack_name = 'Sample-Smart-Home-Backend'
    print('Stack:', cf_stack_name)
    response = cf_aws.describe_stacks(StackName=cf_stack_name)
    datetime_last_modified = response['Stacks'][0]['CreationTime']
    print(cf_stack_name, datetime_last_modified, get_relative_time_string(datetime_last_modified), '\n')

    # Lambda
    lambda_function_name = 'SampleSkillAdapter'
    print('Lambda:', lambda_function_name)
    lambda_endpoint_adapter = lambda_aws.get_function(FunctionName=lambda_function_name)
    datetime_last_modified_string = lambda_endpoint_adapter['Configuration']['LastModified']
    datetime_last_modified = datetime.strptime(datetime_last_modified_string, '%Y-%m-%dT%H:%M:%S.%f%z')
    print(lambda_function_name, datetime_last_modified, get_relative_time_string(datetime_last_modified), '\n')

    # S3 Bucket
    bucket = 'endpoint-code-us'
    key = package_filename
    print('S3 Bucket:', bucket)
    object_endpoint_package = s3_aws.get_object(Bucket=bucket, Key=key)
    datetime_last_modified = object_endpoint_package['LastModified']
    print(bucket, key, datetime_last_modified, get_relative_time_string(datetime_last_modified), '\n')
    return True


def get_relative_time_string(datetime_modified):
    datetime_now = datetime.now(timezone.utc)
    datetime_delta = datetime_modified - datetime_now
    relative_time = divmod(datetime_delta.days * 86400 + datetime_delta.seconds, 60)
    relative_time_string = '{0} minutes and {1} seconds ago'.format(abs(relative_time[0]), relative_time[1])
    return relative_time_string