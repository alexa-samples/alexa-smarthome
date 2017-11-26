import json
import os
import urllib.request
from datetime import datetime, timedelta, timezone
from zipfile import ZipFile

import boto3
from alexa.skills.smarthome import AlexaChangeReport
from alexa.skills.smarthome import AlexaDiscoverResponse
from alexa.skills.smarthome import AlexaError
from alexa.skills.smarthome import AlexaPowerController
from endpoint_cloud import ApiHandler
from endpoint_cloud import ApiResponse
from endpoint_cloud import ApiResponseBody
from endpoint_cloud import ApiUtils
from index import handler
from jsonschema import validate, ValidationError, SchemaError

api_aws = boto3.client('apigateway')
cf_aws = boto3.client('cloudformation')
iot_aws = boto3.client('iot')
lambda_aws = boto3.client('lambda')
s3_aws = boto3.client('s3')

package_filename = 'endpoint-package.zip'
sample_uri = 'https://raw.githubusercontent.com/alexa/alexa-smarthome/master/sample_messages/'


def json_output(dict):
    return print(json.dumps(dict, indent=2))


def test():
    test_error()

    # Handle AuthGrant
    # test_auth_grant()

    # Handle Discovery
    test_discovery()

    # Handle TurnOff
    test_power_controller(state="OFF")

    # Handle TurnOn
    test_power_controller(state="ON")

    # Handle ChangeReport

    # Handle StateReport


def test_error():
    alexa_error = AlexaError()
    json_output(alexa_error.get_response())
    return


# def test_auth_grant():
#     request = get_sample(sample_uri + 'Authorization/Authorization.AcceptGrant.request.json')
#     alexa_authorization = AlexaAuthorization(request)
#     print(alexa_authorization.get_response())
#     return


def test_discovery():
    request = get_sample(sample_uri + 'Discovery/Discovery.request.json')
    alexa_discovery = AlexaDiscoverResponse(request)
    json_output(alexa_discovery.get_response())
    return


def test_change_report(**kwargs):
    alexa_change_report = AlexaChangeReport()
    response = alexa_change_report.get_response()

    json_output(response)
    return


def test_power_controller(**kwargs):
    if kwargs.get('state') == 'ON':
        request = get_sample(sample_uri + 'PowerController/PowerController.TurnOn.request.json')
    else:
        request = get_sample(sample_uri + 'PowerController/PowerController.TurnOff.request.json')

    try:
        # Parse the request
        namespace = request['directive']['header']['namespace']
        value = request['directive']['header']['name']
        payload_version = request['directive']['header']['payloadVersion']
        messageId = request['directive']['header']['messageId']
        correlation_token = None
        if 'correlationToken' in request['directive']['header']:
            correlation_token = request['directive']['header']['correlationToken']
        token = request['directive']['endpoint']['scope']['token']
        endpoint_id = request['directive']['endpoint']['endpointId']

        alexa_power_controller = AlexaPowerController(value=value, token=token, correlation_token=correlation_token, endpoint_id=endpoint_id)
        response = alexa_power_controller.get_response()
    except KeyError as e:
        response = AlexaError(type='KeyError', message=str(e)).get_response()

    json_output(response)
    return


def quick_test():
    request = {}
    request['queryStringParameters'] = {}
    request['queryStringParameters']['state'] = 'SPECIAL'
    state = request['queryStringParameters'].get('state', None)
    print(state)


def get_sample(url):
    content = urllib.request.urlopen(url).read().decode("utf-8")
    return json.loads(content)


def test_api_auth():
    with open('examples/scratch.json', 'r') as request_file:
        request = json.loads(request_file.read())
        response = handler(request, None)
        print(response)


def test_api_utils():
    print(ApiUtils.get_time_utc())


def test_api_response():
    # print(ApiResponse())
    api_response = ApiResponse()
    print(api_response.create())

    api_response = ApiResponse()
    api_response.statusCode = 200
    api_response.body = ApiResponseBody(result="OK", message="GET")
    print(api_response.create())


def test_response_error():
    api_response = ApiResponse()
    key_error = "httpMethod"
    message_string = "KeyError: {0}".format(key_error)
    #  For a key Error, return an error and HTTP Status of 400 Bad Request
    api_response.statusCode = 400
    api_response.body = ApiResponseBody(result="ERR", message=message_string)

    print(api_response)


def handler_endpoint_create():
    with open('examples/request.endpoints.post.body.json', 'r') as request_file:
        request = json.loads(request_file.read())
        api_handler = ApiHandler()
        response = api_handler.endpoint.create(request)
        print(response)


def handler_endpoint_read():
    with open('examples/request.endpoints.get.json', 'r') as request_file:
        request = json.loads(request_file.read())
        api_handler = ApiHandler()
        response = api_handler.endpoint.read(request)
        print(response)


def handler_endpoint_read_id():
    with open('examples/request.endpoints.name.get.json', 'r') as request_file:
        request = json.loads(request_file.read())
        api_handler = ApiHandler()
        response = api_handler.endpoint.read(request)
        print(response)


def handler_event_create():
    with open('examples/request.events.post.json', 'r') as request_file:
        request = json.loads(request_file.read())
        api_handler = ApiHandler()
        response = api_handler.event.create(request)
        print(response)


def test_iot_create():
    attribute_payload = {'attributes': {'operation': 'OFF'}}
    response = iot_aws.create_thing(
        thingName='endpoint_test_001',
        thingTypeName='EndpointSwitch',
        attributePayload=attribute_payload
    )
    print(response)


def validate_response():
    request = get_sample(sample_uri + 'Discovery/Discovery.request.json')
    alexa_discovery = AlexaDiscoverResponse(request)
    # response = json.loads(alexa_discovery.get_response())
    response = alexa_discovery.get_response()

    # sample_response = get_sample(sample_uri + 'Discovery/Discovery.response.json')
    # response = json.dumps(sample_response)

    print(response)

    valid = False
    try:
        with open('alexa_smart_home_message_schema.json', 'r') as schema_file:
            json_schema = json.load(schema_file)
            print(json_schema)
            print(validate(response, json_schema))
        valid = True
    except SchemaError as se:
        print('validate_response: Invalid Schema', se)
    except ValidationError as ve:
        print('validate_response: Invalid Content', ve)

    return valid


def test_iot():
    user_id = '0'
    list_response = iot_aws.list_things(attributeName='userId', attributeValue=user_id)
    # for thing in list_response['things']:
    #     print(thing)
    json_output(list_response)


def test_db_endpoint():
    dynamodb_aws = boto3.resource('dynamodb')
    table = dynamodb_aws.Table('EndpointDetails')
    result = table.put_item(
        Item={
            'DetailsId': '0',
            'ManufacturerName': 'Endpoint Manufacturer',
            'FriendlyName': 'Black Switch',
            'Description': 'A Black Endpoint Switch'
        }
    )
    print(result)


def deploy():
    if not os.path.isfile(package_filename):
        print('ERR', package_filename, 'file not found')
        return

    with open(package_filename, 'rb') as file_data:
        s3_aws.upload_fileobj(file_data, 'endpoint-code-us', package_filename)
        print('Deployed: S3')

    zip_package = open(package_filename, "rb")
    response = lambda_aws.update_function_code(
        FunctionName='SampleEndpointAdapter',
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
        zip_package.write('alexa_smart_home_message_schema.json')
        pack_folder(zip_package, 'alexa')
        pack_folder(zip_package, 'endpoint_cloud')
        pack_folder(zip_package, 'jsonschema')

    print('Ending packaging')
    return


def push():
    pack()
    deploy()


# Get the modification times of the Stack, Lambda, and S3 Bucket
def status():
    # Stack
    cf_stack_name = 'Sample-Smart-Home-Backend'
    print('Stack:', cf_stack_name)
    response = cf_aws.describe_stacks(StackName=cf_stack_name)
    datetime_last_modified = response['Stacks'][0]['CreationTime']
    print(cf_stack_name, datetime_last_modified, get_relative_time_string(datetime_last_modified), '\n')

    # Lambda
    lambda_function_name = 'SampleEndpointAdapter'
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


def test_time(expiration_utc='2017-11-26T10:06:48.00Z'):

    now = datetime.utcnow().replace(tzinfo=None)
    then = datetime.strptime(expiration_utc, "%Y-%m-%dT%H:%M:%S.00Z")

    print('now ', now)
    print('then', then)
    seconds = (now - then).seconds
    print('seconds', seconds)

    is_expired = now > then
    print('is_expired', is_expired)

    is_soon = seconds < 30
    print('is_soon', is_soon)


