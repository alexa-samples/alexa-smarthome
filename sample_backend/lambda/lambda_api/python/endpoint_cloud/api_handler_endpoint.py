# -*- coding: utf-8 -*-

# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Amazon Software License (the "License"). You may not use this file except in
# compliance with the License. A copy of the License is located at
#
#    http://aws.amazon.com/asl/
#
# or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific
# language governing permissions and limitations under the License.

import boto3
import json
import uuid

from botocore.exceptions import ClientError

dynamodb_aws = boto3.client('dynamodb')
iot_aws = boto3.client('iot')


class ApiHandlerEndpoint:
    class EndpointDetails:
        def __init__(self):
            self.capabilities = ''
            self.description = ''
            self.display_categories = ''
            self.friendly_name = ''
            self.id = str(uuid.uuid4())  # Generate an ID for the endpoint
            self.manufacturer_name = ''
            self.sku = 'OT00'
            self.user_id = 0

        def dump(self):
            print('EndpointDetails:')
            print('capabilities:', self.capabilities)
            print('description:', self.description)
            print('display_categories:', self.display_categories)
            print('friendly_name:', self.friendly_name)
            print('id:', self.id)
            print('manufacturer_name:', self.manufacturer_name)
            print('sku:', self.sku)
            print('user_id:', self.user_id)

    def create(self, request):
        try:
            endpoint_details = self.EndpointDetails()

            # Map our incoming API body to a thing that will virtually represent a discoverable device for Alexa
            json_object = json.loads(request['body'])
            endpoint_details.user_id = json_object['event']['endpoint']['userId']  # Expect a Profile
            endpoint_details.friendly_name = json_object['event']['endpoint']['friendlyName']
            endpoint_details.capabilities = json_object['event']['endpoint']['capabilities']  # Capabilities JSON
            endpoint_details.sku = json_object['event']['endpoint']['sku']  # A custom endpoint type, ex: SW01
            endpoint_details.description = json_object['event']['endpoint']['description']
            endpoint_details.manufacturer_name = json_object['event']['endpoint']['manufacturerName']
            endpoint_details.display_categories = json_object['event']['endpoint']['displayCategories']

            # print("LOG endpoint.create.endpoint_details:", endpoint_details.dump())

            # Create the thing in both DynamoDb and AWS IoT
            response = self.create_thing_details(endpoint_details)
            # TODO Check response
            response = self.create_thing(endpoint_details)
            # TODO Check response

            return response

        except KeyError as key_error:
            return "KeyError: " + str(key_error)

    def create_thing(self, endpoint_details):

        # Create the ThingType if missing
        thing_type_name = self.create_thing_type(endpoint_details.sku)

        # TODO Set the Default State
        attribute_payload = {
            'attributes': {
                'user_id': endpoint_details.user_id
            }
        }

        try:
            response = iot_aws.create_thing(
                thingName=endpoint_details.id,
                thingTypeName=thing_type_name,
                attributePayload=attribute_payload
            )
            print('LOG endpoint.create.create_thing ' + str(response))
            return response

        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceAlreadyExistsException':
                print('WARN iot resource already exists, trying update')
                response = iot_aws.update_thing(
                    thingName=endpoint_details.id,
                    thingTypeName=thing_type_name,
                    attributePayload=attribute_payload
                )
                return response

        except Exception as e:
            print(e)

    def create_thing_details(self, endpoint_details):
        dynamodb_aws_resource = boto3.resource('dynamodb')
        table = dynamodb_aws_resource.Table('SampleEndpointDetails')
        response = table.update_item(
            Key={
                'EndpointId': endpoint_details.id
            },
            UpdateExpression='SET \
                    Capabilities = :capabilities, \
                    Description = :description, \
                    DisplayCategories = :display_categories, \
                    FriendlyName = :friendly_name, \
                    ManufacturerName = :manufacturer_name, \
                    SKU = :sku, \
                    UserId = :user_id',
            ExpressionAttributeValues={
                ':capabilities': str(json.dumps(endpoint_details.capabilities)),
                ':description': str(endpoint_details.description),
                ':display_categories': str(json.dumps(endpoint_details.display_categories)),
                ':friendly_name': str(endpoint_details.friendly_name),
                ':manufacturer_name': str(endpoint_details.manufacturer_name),
                ':sku': str(endpoint_details.sku),
                ':user_id': str(endpoint_details.user_id)

            }
        )
        print('LOG endpoint.create_thing_details ' + str(response))
        return response

    def create_thing_group(self, thing_group_name):
        response = iot_aws.create_thing_group(
            thingGroupName=thing_group_name
        )
        print('LOG endpoint.create_thing_group ' + str(response))

    def create_thing_type(self, sku):
        # Set the default at OTHER (OT00)
        thing_type_name = 'SampleOther'
        thing_type_description = 'A sample Other endpoint'

        if sku.upper().startswith('LI'):
            thing_type_name = 'SampleLight'
            thing_type_description = 'A sample light endpoint'

        if sku.upper().startswith('MW'):
            thing_type_name = 'SampleMicrowave'
            thing_type_description = 'A sample microwave endpoint'

        if sku.upper().startswith('SW'):
            thing_type_name = 'SampleSwitch'
            thing_type_description = 'A sample switch endpoint'

        response = iot_aws.create_thing_type(
            thingTypeName=thing_type_name,
            thingTypeProperties={
                'thingTypeDescription': thing_type_description
            }
        )
        print('LOG endpoint.create_thing_type ' + str(response))
        return thing_type_name

    def delete(self, request):
        try:
            response = {}
            print(request)
            json_object = json.loads(request['body'])
            endpoint_ids = []
            delete_all_sample_endpoints = False
            for endpoint_id in json_object:
                # Special Case for * - If any match, delete all
                if endpoint_id == '*':
                    delete_all_sample_endpoints = True
                    break
                endpoint_ids.append(endpoint_id)

            if delete_all_sample_endpoints is True:
                self.delete_samples()
                response = {'message': 'Deleted all sample endpoints'}

            for endpoint_id in endpoint_ids:
                iot_aws.delete_thing(thingName=endpoint_id)
                response = dynamodb_aws.delete_item(TableName='SampleEndpointDetails', Key={'EndpointId': endpoint_id})

            return response

        except KeyError as key_error:
            return "KeyError: " + str(key_error)

    def delete_samples(self):
        table = boto3.resource('dynamodb').Table('SampleEndpointDetails')
        result = table.scan()
        items = result['Items']
        for item in items:
            endpoint_id = item['EndpointId']
            self.delete_thing(endpoint_id)

    def delete_thing(self, endpoint_id):
        # TODO Improve response handling
        # Delete from DynamoDB
        response = dynamodb_aws.delete_item(
            TableName='SampleEndpointDetails',
            Key={'EndpointId': {'S': endpoint_id}}
        )
        print(response)

        # Delete from AWS IoT
        response = iot_aws.delete_thing(
            thingName=endpoint_id
        )
        print(response)

    def read(self, request):
        try:
            response = {}
            resource = request['resource']
            if resource == '/endpoints':
                list_response = iot_aws.list_things()
                status = list_response['ResponseMetadata']['HTTPStatusCode']
                if 200 <= int(status) < 300:
                    things = list_response['things']
                    response = []
                    for thing in things:
                        response.append(thing)
            else:
                path_parameters = request['pathParameters']
                endpoint_name = path_parameters['endpoint_name']
                response = iot_aws.describe_thing(thingName=endpoint_name)

            print('LOG endpoint.read ' + str(response))
            return response

        except KeyError as key_error:
            return "KeyError: " + str(key_error)

